from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cleanfusion",
    version="0.1.6",
    author="Hriday Thaker, Himanshu Chopade, Gautam Rajhans, Aryan Bachute", 
    author_email="hriday.thaker2604@gmail.com, himanshuchopade97@gmail.com, gprajhans@gmail.com, bachutearyan@gmail.com",  
    description="A comprehensive data cleaning and preprocessing library for structured and unstructured data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/himanshuchopade97/CleanFusion",  # Replace with your GitHub URL
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "numpy>=1.20.0",
        "nltk>=3.6.0",
        "scipy>=1.7.0",
        "python-docx>=0.8.11",
        "PyPDF2>=2.0.0",
        "sentence-transformers>=2.2.0",
        "category-encoders>=2.3.0",
    ],
    extras_require={
        "transformers": ["transformers>=4.15.0", "torch>=1.10.0"],
        "full": [
            "transformers>=4.15.0",
            "torch>=1.10.0",
            "spacy>=3.0.0",
            "pytesseract>=0.3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "cleanfusion=cleanfusion.cli:main",
        ],
    },
)