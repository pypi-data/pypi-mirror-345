from setuptools import setup, find_packages

setup(
    name="custom_base_django",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=4.2",
        "djangorestframework",
        "djangorestframework-simplejwt",
        "jdatetime",
        "elasticsearch_dsl",
    ],
    description="A custom Django library with models, views, and URLs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/k-hesamoddin/custom_base_django",
    author="Kourosh Hesamoddin",
    author_email="k.hesamoddin@gmail.com",
    license="MICMOD",
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
