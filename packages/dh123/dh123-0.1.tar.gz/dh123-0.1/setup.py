from setuptools import setup

setup(
    name="dh123",
    version="0.1",
    packages=["dh123"],
    entry_points={
        'console_scripts': [
            'dh123=dh123.download_file:download',
        ],
    },
    author="Rajesh",
    description="Download DH.Java from GitHub",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    python_requires=">=3.6",
)
