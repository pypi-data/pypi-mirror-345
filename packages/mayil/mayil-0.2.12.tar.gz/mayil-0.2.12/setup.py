from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mayil",
    version="0.2.12",
    author="Aravind Suresh",
    author_email="your.email@example.com",
    description="A Python library for generating beautiful HTML emails",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mayil",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandas>=1.0.0",
        "jinja2>=2.11.0",
        "premailer>=3.10.0",
        "markdown2>=2.4.0",
    ],
    include_package_data=True,
    package_data={
        "mayil": [
            "templates/*.html",
            "static/*.css",
            "static/*.js",
        ],
    },
) 