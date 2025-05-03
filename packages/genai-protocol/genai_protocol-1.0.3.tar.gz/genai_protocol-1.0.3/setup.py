from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="genai-protocol",
    version="1.0.3",
    description="GenAI Python project for agents connector library that integrates with GenAI infrastructure",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Yaroslav Oliinyk, Valentyn Slivko, Ivan Kuzlo",
    author_email="yaroslav.oliinyk@chisw.com, valentyn.slivko@chisw.com, ivan.kuzlo@chisw.com",
    url="https://github.com/genai-works-org/genai-protocol",
    readme="README.md",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    license="Apache License 2.0",
    install_requires=[
        "aiohappyeyeballs>=2.6.1",
        "aiohttp>=3.11.16",
        "aiosignal>=1.3.2",
        "annotated-types>=0.7.0",
        "attrs>=25.3.0",
        "frozenlist>=1.5.0",
        "idna>=3.10",
        "multidict>=6.2.0",
        "propcache>=0.3.1",
        "pydantic>=2.11.1",
        "pydantic-core>=2.33.0",
        "typing-extensions>=4.13.0",
        "typing-inspection>=0.4.0",
        "websockets>=15.0.1",
        "yarl>=1.18.3",
        "pyjwt>=2.10.1",
    ],
    extras_require={
        "dev": ["twine>=6.1.0"],
    },
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
