"""Package setup for envault."""

from setuptools import find_packages, setup

setup(
    name="envault",
    version="0.1.0",
    description="Securely store and sync .env files using encrypted backends.",
    author="envault contributors",
    python_requires=">=3.9",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "cryptography>=41.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov",
        ]
    },
    entry_points={
        "console_scripts": [
            "envault=envault.cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS :: Independent",
    ],
)
