from setuptools import setup, find_packages

setup(
    name="serve-secrets",
    version="1.2.2",
    description="A tool to store and retrieve API keys using the system's password manager.",
    author="Samanvay Yagsen",
    author_email="samanvaya.yagsen@gmail.com",
    url="https://github.com/samanvaya/serve-secrets",
    packages=find_packages(include=["serve_secrets", "serve_secrets.*"]),
    install_requires=[
        "keyring",
        "pyperclip",
    ],
    entry_points={
        "console_scripts": [
            "serve-secrets=serve_secrets.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)