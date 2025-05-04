import logging
import os
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import lru_cache
from typing import List, Optional, Union

import boto3
from botocore.exceptions import ClientError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jinja2 import Environment, PackageLoader
from jose import JWTError, jwt
from passlib.context import CryptContext
from tortoise.exceptions import IntegrityError

from . import models, schemas

admin_client = os.getenv("ADMIN_CLIENT", "admin")
algorithm = "HS256"
aws_region = os.getenv("AWS_DEFAULT_REGION")
env = Environment(loader=PackageLoader("epona", "auth"))
host = os.getenv("HOST_URL")
log = logging.getLogger("uvicorn")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
secret_key = os.getenv(
    "SECRET_KEY", "7a086308aff6f391b190ece729f81fdbe564efa21153cc99ce659be0ddcea596"
)


def valid_client(client: str) -> bool:
    """Verifica se é um client_id ou username válido"""
    if len(client) < 3 or len(client) > 20:
        return False
    if client.count(" ") > 0:
        return False
    return True


def valid_email(email: str) -> bool:
    """Verifica se a string é um email válido"""
    chars = ["@", ".", " "]
    at = 0
    dot = 0
    space = 0
    for c in chars:
        if c == "@":
            at = email.count(c)
        elif c == ".":
            dot = email.count(c)
        elif c == " ":
            space = email.count(c)
    if at == 1 and dot >= 1 and space == 0:
        return True
    return False


def valid_password(password: str) -> bool:
    """Verifica se a string é uma senha válida"""
    if len(password.strip()) < 6:
        return False
    if len(password.strip()) > 100:
        return False
    return True


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """verifica criptografia da senha"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """criptografa senha"""
    return pwd_context.hash(password)


async def get_user(client_id: str, username: str) -> Union[schemas.UserSchema, None]:
    """recebe um client_id e username e retorna o usuario"""
    user = await models.User.filter(client_id=client_id, username=username)
    if not user:
        return None
    return schemas.UserSchema(**dict(user[0]))


async def get_user_with_pass(
    username: str, client: str
) -> Union[schemas.UserSchema, None]:
    """Autentica o usuario e retorna usuario e suas permissões"""
    user = (
        await models.User.filter(username=username, client_id=client)
        .prefetch_related("permissions")
        .first()
    )

    if not user:
        return None

    permissions = await user.permissions.all()
    permissions_list = []
    for perm in permissions:
        await perm.fetch_related("permission")
        permissions_list.append(perm.permission.name)
    user.scope = user.scope + " " + " ".join(permissions_list)
    return schemas.UserSchema(**dict(user))


async def authenticate_user(
    username: str, password: str, client_id: str
) -> Union[schemas.UserSchema, None]:
    """Faz o login do usuairo"""
    user = await get_user_with_pass(username, client_id)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


async def save(payload: schemas.UserSchema) -> Union[schemas.UserSchema, None]:
    """Salva um novo usuário e configura o client_id"""
    user = models.User(
        active=payload.active,
        client_id=payload.client_id,
        email=payload.email,
        username=payload.username,
        password_hash=payload.password_hash,
    )
    if (
        not valid_email(user.email)
        or not valid_password(user.password_hash)
        or not valid_client(user.client_id)
        or not valid_client(user.username)
    ):
        return None

    client = await models.Client.filter(name__iexact=payload.client_id).first()
    if payload.client_id in admin_client:
        user.scope = "admin super-admin"
    else:
        user.scope = "user pessoas:create"
    if not client:
        user.scope = "admin" if "admin" not in user.scope else user.scope
        await user.save()
        client = models.Client(
            name=payload.client_id,
            active=True,
            valid_domains=payload.email.split("@")[1],
            activity_sectors_id=payload.sector,
        )
        await client.save()
        permissions = await models.Permission.all()
        scopes = ""
        for permission in permissions:
            user_permission = models.UserPermission(
                client_id=user.client_id,
                entities="all",
                user=user,
                permission=permission,
            )
            await user_permission.save()
            scopes += f" {permission.name}"
        user.scope = user.scope + scopes
    elif (
        client.multiple_domains
        or client.valid_domains
        and user.email.split("@")[1] in client.valid_domains
    ):
        await user.save()
        # permite que o usuario possa criar pessoas do usuario
        permission = await models.Permission.filter(name="pessoas:create").first()
        user_permission = models.UserPermission(
            client_id=client.id, entities="all", user=user, permission=permission
        )
        await user_permission.save()
    else:
        return None
    return schemas.UserSchema(**dict(user))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """cria token de acesso"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60 * 10)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


async def get_current_user(
    security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)
) -> schemas.UserSchema:
    """Verifica permissões de segurança do usuário"""
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Usuário ou senha inválidos",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", "")
        token_data = schemas.TokenData(username=username, scopes=token_scopes.split())
    except JWTError as err:
        log.error(f"JWT error: {err}")
        raise credentials_exception
    client_id, username = token_data.username.split(":")
    user = await get_user(client_id=client_id, username=username)
    if user is None:
        raise credentials_exception
    # verifica permissoes quando o usuario nao é admin
    if "admin" not in token_scopes:
        for scope in security_scopes.scopes:
            if scope not in token_data.scopes:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Acesso não autorizado",
                    headers={"WWW-Authenticate": authenticate_value},
                )
    user.scope = token_scopes
    return user


async def get_current_active_user(
    current_user: schemas.UserSchema = Depends(get_current_user),
) -> schemas.UserSchema:
    """Verifica se o usuário está listado como ativo"""
    if not current_user.active:
        raise HTTPException(status_code=400, detail="Usuário desativado")
    return current_user


async def entity_access(
    perm_name: str, entity_id: str, user: schemas.UserSchema
) -> bool:
    """
    Verifica se um usuário tem permissão para manipular uma entidade específica
    O esquema de uma permissão é o nome da permissão seguido da ação. exemplo:
    perm_name: create
    perm_name é o nome da entidade
    create é a ação
    """
    log.info("Verificando permissões na entidade %s: %s. Usuário: %s" % (perm_name, entity_id, user.id))
    user_wp = (
        await models.User.filter(client_id=user.client_id, id=user.id)
        .first()
        .prefetch_related("permissions")
    )
    if not user_wp:
        return False
    for permission in user_wp.permissions.related_objects:
        await permission.fetch_related("permission")
        if permission.permission.name == perm_name:
            if permission.entities == "all":
                return True
            for entity in permission.entities.split():
                if entity == entity_id:
                    return True
    return False


@lru_cache(maxsize=8)
async def user_permissions(client_id, user_id) -> models.User:
    """Traz um usuario com suas permissões"""
    result = (
        await models.User.filter(client_id=client_id, id=user_id)
        .first()
        .prefech_related("permissions")
    )
    return result


async def user_add_permission(
    payload: schemas.UserPermissionPayloadSchema, admin: schemas.UserSchema
) -> int:
    """Salva novas permissões do usuario e retorna o número de permissões salvas"""
    saved = 0
    user = await models.User.filter(
        username=payload.username, client_id=admin.client_id
    ).first()
    for name in payload.permissions:
        permission = await models.Permission.filter(name=name).first()
        if not permission or not user:
            continue

        user_permission = await models.UserPermission.filter(
            client_id=admin.client_id, user_id=user.id, permission_id=permission.id
        ).first()
        if user_permission:
            user_permission.entities = " ".join(payload.entities)
        else:
            user_permission = models.UserPermission(
                client_id=admin.client_id,
                permission=permission,
                user=user,
                entities=" ".join(payload.entities),
            )
        try:
            await user_permission.save()
            saved += 1
        except IntegrityError:
            user_permission = await models.UserPermission.filter(
                client_id=payload.client_id,
                user_id=user.id,
                permission_id=permission.id,
            ).first()
            if not user_permission:
                continue
            user_permission.entities = " ".join(payload.entities)
            await user_permission.save()
            saved += 1
    return saved


async def add_permission(payload: schemas.PermissionSchema) -> bool:
    """Cria permissões do usuário"""
    permission = models.Permission(name=payload.name, description=payload.description)
    await permission.save()
    if not permission.id:
        raise HTTPException
    # adiciona a nova permissao para usuarios administradores
    admin_users = await models.User.filter(scope="admin").all()
    for user in admin_users:
        user_perm = schemas.UserPermissionPayloadSchema(
            client_id=user.client_id,
            entities=["all"],
            permissions=[permission.name],
            username=user.username,
        )
        user_schema = schemas.UserSchema(**dict(user))
        await user_add_permission(user_perm, user_schema)
    return True


async def get_users(admin: schemas.UserSchema) -> Optional[List[schemas.UserSchema]]:
    """Retorna lista de usuários salvos"""
    users = await models.User.filter(client_id=admin.client_id).all()
    if not users:
        return None
    return [schemas.UserSchema(**dict(user)) for user in users]


async def get_user_detail(
    username: str, admin: schemas.UserSchema
) -> Optional[schemas.UserPermissionResponseSchema]:
    """Mostra permissões de um usuário para o administrador"""
    user = await models.User.filter(
        username=username, client_id=admin.client_id
    ).first()
    if not user:
        return None
    await user.fetch_related("permissions")
    permissions_list = []
    for perm in user.permissions:
        await perm.fetch_related("permission")
        perm_dict = dict(perm)
        perm_dict["name"] = perm.permission.name
        perm_dict["description"] = perm.permission.description
        permissions_list.append(perm_dict)
    user_dict = dict(user)
    uwp = schemas.UserPermissionResponseSchema(
        **{**user_dict, "permissions": permissions_list}
    )
    return uwp


async def delete(username: str, admin: schemas.UserSchema) -> bool:
    """Deleta o usuário pelo administrador"""
    user = await models.User.filter(
        username=username, client_id=admin.client_id
    ).first()
    if not user:
        return False
    await user.delete()
    return True


async def update(
    payload: schemas.UserForm, admin: schemas.UserSchema
) -> schemas.UserForm:
    """Atualiza dados cadastrais do usuario"""
    user = await models.User.filter(
        username=payload.username, client_id=admin.client_id
    ).first()

    # TODO: refatorar trocando ternario por if normal
    user.active = (
        payload.active
        if (payload.active or not payload.active) and "admin" in admin.scope
        else user.active
    )
    user.scope = (
        payload.scope
        if payload.scope in ["user", "admin"] and "admin" in admin.scope
        else "user"
    )
    user.email = (
        payload.email
        if valid_email(payload.email) and "admin" in admin.scope
        else user.email
    )
    if valid_password(payload.password) and (
        user.username == admin.username or "admin" in admin.scope
    ):
        user.password_hash = get_password_hash(payload.password)

    await user.save()
    return schemas.UserForm(**{**dict(user), "password": ""})


async def exclude_entity_permission(entity_name: str, pk: str):
    """Exclui uma entidade da lista de permissões de todos os usuários"""
    log.info("Excluindo permissões de %s: %s." % (entity_name, pk))
    permissions = await models.Permission.filter(name__startswith=entity_name).all()
    for perm in permissions:
        users_permissions = await models.UserPermission.filter(
            permission_id=perm.id
        ).all()
        for user_p in users_permissions:
            entities = user_p.entities.split()
            if entities.count(pk) > 0:
                entities.remove(pk)
                user_p.entities = " ".join(entities)
                await user_p.save()


async def include_entity_permission(
    entity_name: str, pk: str, user: schemas.UserSchema
):
    """Inclui uma entidade na lista de entidades que o usuário pode editar"""
    log.info("Incluindo permissões em %s: %s. %s" % (entity_name, pk, user.id))
    permissions = await models.Permission.filter(name__startswith=entity_name).all()
    for perm in permissions:
        users_permissions = await models.UserPermission.filter(
            permission_id=perm.id, user_id=user.id
        ).all()
        for user_p in users_permissions:
            if user_p.entities != "all":
                user_p.entities = user_p.entities + f" {pk}"
                await user_p.save()


async def get_permissions() -> List[schemas.PermissionSchema]:
    """Lista todas as permissões salvas"""
    permissions = await models.Permission.filter().all()
    return [schemas.PermissionSchema(**dict(perm)) for perm in permissions]


async def delete_user_permission(payload: schemas.UserPermissionPayloadSchema) -> int:
    """Deleta permissões de um usuário por um administrador"""
    user = await models.User.filter(username=payload.username).first()
    deleted = 0
    for permission in payload.permissions:
        perm = await models.Permission.filter(name=permission).first()
        user_perm = await models.UserPermission.filter(
            user_id=user.id, permission_id=perm.id
        ).first()
        if user_perm:
            await user_perm.delete()
            deleted += 1
    return deleted


def send_email(payload: schemas.EmailPayload):
    """Envia email para usuario"""
    client = boto3.client("ses", region_name=aws_region)

    # Cria o cabecalho e-mail
    msg = MIMEMultipart("mixed")
    msg["Subject"] = payload.subject
    msg["From"] = payload.sender
    msg["To"] = payload.recipient

    # Cria o conteudo multipart filho
    msg_body = MIMEMultipart("alternative")

    # Codifica o texto e o HTML para o padrao definido em CHARSET
    text_part = MIMEText(
        payload.body_text.encode(payload.charset), "plain", payload.charset
    )
    html_part = MIMEText(
        payload.html_text.encode(payload.charset), "html", payload.charset
    )

    msg_body.attach(text_part)
    msg_body.attach(html_part)

    # inclui o body na mensagem
    msg.attach(msg_body)

    try:
        response = client.send_raw_email(
            Source=payload.sender,
            Destinations=[payload.recipient],
            RawMessage={
                "Data": msg.as_string(),
            },
        )
    except ClientError as err:
        print(err.response["Error"]["Message"])
    else:
        return response


async def password_recover(
    payload: schemas.PasswordRecoverPayload,
    template_path: str
) -> schemas.EmailResponse:
    """Formato do email de recuperação de senha"""
    user = await models.User.filter(
        email=payload.email, client_id=payload.client_id
    ).first()
    if user is None:
        raise HTTPException(
            404,
            f"Não foi encontrado nenhum usuário com o e-mail '{payload.email}' "
            f"na empresa '{payload.client_id}'",
        )
    expires = timedelta(minutes=15)
    recover_token = create_access_token({"email": user.email}, expires)
    template = env.get_template(template_path)
    context = {
        "token": recover_token,
        "host": host,
        "username": user.username,
    }
    # noqa: W291
    param = schemas.EmailPayload(
        **{
            "sender": "Sigeli Epona <sigeli@eponaconsultoria.com.br>",
            "recipient": user.email,
            "subject": "Recuperação de senha",
            "body_text": f"Olá {user.username},\n\nPara recuperar sua senha clique "
            f"aqui: <{host}/recuperar-senha?{recover_token}>\n"
            f"Em caso de problemas com o link, acessa a pagina "
            f"<{host}/recuperar-senha>"
            f"e utilize este token '{recover_token}' para fazer a alteração de "
            f"sua senha. As aspas não fazem parte do token.\n\nSigeli",
            "html_text": template.render(context),
            "charset": "utf-8",
        }
    )
    resp = send_email(param)
    if not resp:
        raise HTTPException(404, "Falha no envio do e-mail.")
    return schemas.EmailResponse(
        **{
            "msg": "E-mail de recuperação enviado com sucesso",
            "status": "OK",
        }
    )


async def recovering(form_data: schemas.ChangePassword) -> schemas.EmailResponse:
    """Recupera senha de acesso do usuário"""
    try:
        token = jwt.decode(form_data.token, secret_key, algorithms=[algorithm])
    except JWTError:
        raise HTTPException(401, "Token inválido")
    if not valid_password(form_data.password):
        raise HTTPException(401, "Senha inválida. Coloque uma senha mais forte")
    if form_data.password != form_data.password_confirm:
        raise HTTPException(401, "Senhas não conferem")

    user = await models.User.filter(
        username=form_data.username, client_id=form_data.client_id, email=token["email"]
    ).first()
    if not user:
        raise HTTPException(401, "Usuário não encontrado")
    user.password_hash = get_password_hash(form_data.password)
    try:
        await user.save()
    except Exception as ex:
        print(ex)
    return schemas.EmailResponse(
        **{"msg": "Senha alterada com sucesso", "status": "OK"}
    )


async def change_password(
    form_data: schemas.ChangePassword, user: schemas.UserSchema
) -> schemas.EmailResponse:
    """Troca senha do usuário"""
    if not valid_password(form_data.password):
        raise HTTPException(401, "Senha inválida. Coloque uma senha mais forte")
    if form_data.password != form_data.password_confirm:
        raise HTTPException(401, "Senhas não conferem")
    user_wp = await models.User.filter(id=user.id).first()
    if user_wp is None:
        raise (401, "Usuário não encontrado")
    user_wp.password_hash = get_password_hash(form_data.password)
    try:
        await user_wp.save()
    except Exception as ex:
        print(ex)
    return schemas.EmailResponse(
        **{"msg": "Senha alterada com sucesso", "status": "OK"}
    )
