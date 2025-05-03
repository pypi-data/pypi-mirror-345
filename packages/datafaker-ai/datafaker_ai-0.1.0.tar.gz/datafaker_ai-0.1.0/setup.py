from setuptools import setup, find_packages

setup(
    name="datafaker_ai",                   # This name must be unique on PyPI
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "google-generativeai"
    ],
    author="Ahsan Raza",
    author_email="ahsanraza1457@email.com",
    description="Generate synthetic data using Gemini and pandas",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/datafaker_ai",  # (Optional)
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
