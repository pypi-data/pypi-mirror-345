from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pybriiv",
    version="0.1.0",
    author="FiveCreate",
    author_email="author@example.com",
    description="Python library for communicating with Briiv Air Purifier devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FiveCreate/pybriiv",
    project_urls={
        "Bug Tracker": "https://github.com/FiveCreate/pybriiv/issues",
        "Documentation": "https://github.com/FiveCreate/pybriiv",
        "Source Code": "https://github.com/FiveCreate/pybriiv",
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Home Automation",
    ],
    python_requires=">=3.9",
)
