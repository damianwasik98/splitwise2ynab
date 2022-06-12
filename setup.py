from setuptools import find_packages, setup


def get_requirements():
    with open("requirements.txt", "r") as f:
        return [l.strip() for l in f.readlines()]


setup(
    name="splitwise2ynab",
    version="0.1.0",
    python_requires=">3.10",
    packages=find_packages(),
    install_requires=get_requirements(),
    entry_points={
        "console_scripts": ["splitwise2ynab=splitwise2ynab.cli.main:cli"]
    },
)
