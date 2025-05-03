from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()


setup(
    name="custom_package1234567",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        #This is used to define the external packages requried to run the custom package
    ],
    entry_points={
        "console_scripts":[
            "hello=src:hello",
            "bye=src:bye"
        ]
    },
    long_description=description,
    long_description_content_type="text/markdown"
)