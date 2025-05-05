
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="postman2openapi",
    version="1.0.0",
    author="Pulkit-Py",
    author_email="pulkitsaini127@gmail.com",  # Replace with your email
    description="A Python module to convert Postman collections to OpenAPI/Swagger format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Pulkit-Py/postman2openapi",  # Replace with your repository URL
    project_urls={
        "Bug Tracker": "https://github.com/Pulkit-Py/postman2openapi/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Documentation",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7",
    install_requires=[
        "pyyaml>=5.1",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "isort>=5.0",
            "flake8>=3.9",
        ],
    },
)