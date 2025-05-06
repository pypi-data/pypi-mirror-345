from setuptools import setup, find_packages
from version_util import get_version

version_publish = get_version("0.0.1", "dev")
print(f"Version Publish: {version_publish}")

setup(
    name="dev-nectarpy",
    version=version_publish,
    packages=find_packages(),
    include_package_data=True,
    license="Apache License 2.0",
    description="A Python API module designed to run queries on Nectar",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/NectarProtocol/python-nectar-module",
    author="Tamarin Health",
    author_email="phil@tamarin.health",
    package_data={
        "": ["*.json"],
        "": ["config/*.json"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11.6,<3.12",
    install_requires=["web3<7.0.0", "python-dotenv==1.1.0", "hpke==0.3.2", "dill==0.3.9"],
)
