# setup.py
from setuptools import setup, find_packages

setup(
    name="dieforyou",
    version="0.1",
    description="A simple Q&A content package",
    author="sungjinwhoo",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
