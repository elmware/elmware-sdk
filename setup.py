import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="elmsdk",
    version="0.0.2",
    author="Elmware",
    author_email="support@elmware.com",
    description="SDK for running docker containers on elmware",
    license='MIT',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/elmware/elmware-sdk",
    packages=setuptools.find_packages(),
    install_requires=[
          'requests',
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)