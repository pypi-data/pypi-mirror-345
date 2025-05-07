from setuptools import setup, find_packages

setup(
    name="synthai-generator",
    version="0.1.0",
    author="Biswanath Roul",
    description="A framework for generating synthetic data using LLMs with techniques to ensure diversity and reduce bias",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/biswanathroul/synthai",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Development Status :: 3 - Alpha",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "transformers>=4.15.0",
        "torch>=1.9.0",
        "scikit-learn>=1.0.0",
        "tqdm>=4.62.0",
        "datasets>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.5b2",
            "isort>=5.9.1",
            "flake8>=3.9.2",
        ],
    },
    # Add CLI entry point
    entry_points={
        "console_scripts": [
            "synthai=synthai.cli:main",
        ],
    },
)