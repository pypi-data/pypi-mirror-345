from setuptools import setup

setup(
    name="rfc123",
    version="0.1",
    packages=["rfc123"],
    entry_points={
        'console_scripts': [
            'rfc123=rfc123.download_file:download',
        ],
    },
    author="Rajesh",
    description="Download RFC.Java from GitHub",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    python_requires=">=3.6",
)
