from setuptools import find_packages, setup

setup(
    name="SmartSecurityPy",
    version="1.0.0",
    description="🔐 Biblioteca de utilidades para hash de senha, criptografia e JWT em Python",
    author="Roberto Lima",
    author_email="robertolima.izphera@gmail.com",
    packages=find_packages(),
    python_requires=">=3.7",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "passlib[bcrypt]",
        "cryptography",
        "PyJWT"
    ],
    keywords=["seguranca", "criptografia", "jwt", "hash", "senha", "python"],
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    project_urls={
        "Homepage": "https://github.com/robertolima-dev/SmartLogs", # noqa501
        "Repository": "https://github.com/robertolima-dev/SmartLogs", # noqa501
        "Issues": "https://github.com/robertolima-dev/SmartLogs/issues", # noqa501
    },
)
