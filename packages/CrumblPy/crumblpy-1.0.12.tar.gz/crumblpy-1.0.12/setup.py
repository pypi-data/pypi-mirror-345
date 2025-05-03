from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='CrumblPy',
    version='1.0.12',
    packages=find_packages(),
    author='Crumbl Data Team',
    author_email='steven.wang@crumbl.com',
    description='Common utility functions for Crumbl Data Team',
    long_description=long_description,  
    long_description_content_type='text/markdown',
    python_requires='>=3.9',
    install_requires=[
        'cryptography==40.0.2',
        'google_api_python_client>=2.125.0',
        'numpy>=1.26.0',
        'pandas==2.2.3',
        'prefect==3.0.3',
        'protobuf==4.25.5',
        'pyarrow==15.0.0',
        'slack_sdk==3.21.3',
        'snowflake-connector-python==3.15.0'
    ]
)