from setuptools import setup, find_packages

setup(
    name="serve-secrets",
    version="1.0.0",
    description="A tool to store and retrieve API keys using the system's password manager.",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/serve-secrets",
    packages=find_packages(),
    install_requires=[
        "keyring",
    ],
    entry_points={
        "console_scripts": [
            "serve-secrets=main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)