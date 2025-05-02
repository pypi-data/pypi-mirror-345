from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="termux-api-python",
    version="0.1.1",
    author="hasanfq6",
    author_email="hasanfq818@gmail.com",
    description="A Python wrapper for the Termux API commands",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Kamanati/termux-api-python",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Android",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.6",
    keywords="termux, android, api, wrapper",
)
