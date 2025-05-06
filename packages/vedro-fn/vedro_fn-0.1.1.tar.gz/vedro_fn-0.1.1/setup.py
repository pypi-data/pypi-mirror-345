from setuptools import find_packages, setup


def find_required():
    with open("requirements.txt") as f:
        return f.read().splitlines()


def find_dev_required():
    with open("requirements-dev.txt") as f:
        return f.read().splitlines()


setup(
    name="vedro-fn",
    version="0.1.1",
    description="Enables a functional-style syntax for defining Vedro scenarios",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Nikita Tsvetkov",
    author_email="tsv1@fastmail.com",
    python_requires=">=3.9",
    url="https://github.com/vedro-universe/vedro-fn",
    project_urls={
        "Docs": "https://github.com/vedro-universe/vedro-fn",
        "GitHub": "https://github.com/vedro-universe/vedro-fn",
    },
    license="Apache-2.0",
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={"vedro_fn": ["py.typed"]},
    install_requires=find_required(),
    tests_require=find_dev_required(),
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Typing :: Typed",
    ],
)
