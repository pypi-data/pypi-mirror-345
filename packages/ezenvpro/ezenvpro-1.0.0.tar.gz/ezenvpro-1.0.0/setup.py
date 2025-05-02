from setuptools import setup, find_packages

setup(
    name="ezenvpro",
    version="1.0.0",
    author="Dominic Thirshatha",
    description="Infra Pentest Environment Manager",
    packages=find_packages(),
    install_requires=["colorama"],
    entry_points={
        "console_scripts": [
            "ezenvpro = ezenvpro.main:cli"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
