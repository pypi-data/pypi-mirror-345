from setuptools import setup, find_packages

setup(
    name="chargedPlanner",
    packages=find_packages(where="src"),  # Tells setuptools to look inside src/
    package_dir={"": "src"},  # Maps src/ to the root package namespace
)