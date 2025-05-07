from setuptools import setup, find_packages

PKG = "nhmail"
version = "1.0.8"
long_desc = (
    """This SDK is a programatic inteface into the mail APIs of NandH Logistics."""
)

setup(
    name=PKG,
    version=version,
    description="email of nandh SDK for Python",
    author="it@nandhlogistics.vn",
    author_email="it@nandhlogistics.vn",
    url="https://github.com/ITNHL/nh-mail-sdk",
    license="Version 1.0",
    packages=find_packages(),
    provides=[PKG],
    test_suite="tests",
    long_description=long_desc,
    install_requires=[
        "pre-commit==3.6.2",
        "marshmallow==3.19.0",
        "requests==2.31.0",
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
    ],
)
