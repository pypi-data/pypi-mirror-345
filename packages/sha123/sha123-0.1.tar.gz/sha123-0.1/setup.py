from setuptools import setup

setup(
    name="sha123",
    version="0.1",
    packages=["sha123"],
    entry_points={
        'console_scripts': [
            'sha123=sha123.download_file:download',
        ],
    },
    author="Rajesh",
    description="Download SHA.Java from GitHub",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    python_requires=">=3.6",
)
