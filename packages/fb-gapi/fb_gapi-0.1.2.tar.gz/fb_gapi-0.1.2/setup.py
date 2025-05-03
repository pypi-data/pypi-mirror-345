from setuptools import setup, find_packages

setup(
    name="fb-gapi",
    version="0.1.2",
    author="Jayed",
    author_email="jayedbinjahangir@gmail.com",
    description="A lightweight Python Sync / Async SDK for sending messages via Facebook Messenger",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jayeeed/facebook-messenger-sdk",
    packages=find_packages(),
    install_requires=["requests", "httpx", "aiofiles", "httpx-retries"],
    python_requires=">=3.6",
)
