from setuptools import setup, find_packages

setup(
    name="dataflow-core",
    version="2.0.7",
    packages=find_packages(include=["dataflow", "dataflow.*", "authenticator", "authenticator.*"]),
    include_package_data=True,
    package_data={
        "dataflow": ["scripts/*.sh"],
    },
    install_requires=[
        'sqlalchemy',
        'boto3',
        'psycopg2-binary',
        'pymysql',
        'requests'
    ],
    author="Dataflow",
    author_email="",
    description="Dataflow core package",
    entry_points={
        'jupyterhub.authenticators': [
            'dataflow_authenticator = authenticator.dataflowhubauthenticator:DataflowHubAuthenticator',
        ],
    },
)
