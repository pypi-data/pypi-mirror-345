from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tax_calculator_by_yousaf",
    version="0.2.1",
    author="Yousaf Khamza",
    author_email="yousaf@example.com",  # Replace with your actual email
    description="A simple calculator to compute income tax for India FY 2025-26",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yousafkhamza/tax_calculator_by_yousaf",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "tax-calculator=tax_calculator.calculator:main",
        ],
    },
)