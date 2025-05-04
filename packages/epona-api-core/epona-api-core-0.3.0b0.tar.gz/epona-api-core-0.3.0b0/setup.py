
import io
import os

from setuptools import setup, find_packages

# Package metadata
NAME = "epona-api-core"
DESCRIPTION = "Epona API-Core"
EMAIL = "marcos@eponaconsultoria.com.br"
AUTHOR = "Antonio Marcos"
REQUIRES_PYTHON = ">=3.9.0"
VERSION = "0.3.0-beta.0"

# Required packages
REQUIRED = [
    "fastapi==0.95.2",
    "asyncpg==0.27.0",
    "boto3==1.28.18",
    "jinja2==3.1.2",
    "pydantic==1.10.7",
    "python-multipart==0.0.6",
    "python-jose==3.3.0",
    "tortoise-orm==0.19.3",
    "passlib[bcrypt]",
]

current_dir = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as long-description
try:
    with io.open(os.path.join(current_dir, "README.md"), encoding="utf-8") as f:
        long_description = f"\n{f.read()}"
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(current_dir, project_slug, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION

setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    packages=find_packages(exclude=["test_"]),
    install_requires=REQUIRED,
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.9",
    ],
    setup_requires=['wheel']
)
