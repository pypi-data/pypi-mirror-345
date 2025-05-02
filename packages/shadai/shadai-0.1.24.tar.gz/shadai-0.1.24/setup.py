from setuptools import find_packages, setup

setup(
    name="shadai",
    version="0.1.24",
    packages=find_packages(),
    install_requires=[
        "boto3==1.35.36",
        "botocore==1.35.36",
        "pydantic==2.9.2",
        "python-dotenv==1.0.1",
        "urllib3==2.2.3",
        "requests==2.32.3",
        "setuptools==75.3.0",
        "tqdm==4.67.1",
        "rich==13.9.4",
    ],
    author="SHADAI GROUP",
    author_email="noreply@shadai.ai",
    description="SHADAI Client",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    package_dir={"shadai": "shadai"},
)
