from setuptools import find_packages, setup

setup(
    name="SimpleFastCrud",
    version="0.1.3",
    packages=find_packages(),
    install_requires=["fastapi", "pydantic", "sqlalchemy"],
    entry_points={},
    )
