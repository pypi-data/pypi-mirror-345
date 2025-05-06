from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="datafaker_ai",
    version="0.1.5",  # bump the version number
    author="Ahsan Raza",
    author_email="your.email@example.com",
    description="Generate synthetic datasets from natural language using Gemini 1.5 Flash",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ahsanraza1457/deepfaker_ai",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "python-dotenv",
        "google-generativeai"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.8',
)
