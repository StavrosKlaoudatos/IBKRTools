from setuptools import setup, find_packages

# Read the README for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    # Package metadata
    name="ibkrtools",
    version="0.1.0",
    author="Stavros Klaoudatos",
    author_email="stavrosklaoudatos@gmail.com",
    description="A modern Python wrapper for Interactive Brokers TWS API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/StavrosKlaoudatos/IBKRTools",
    
    # Package structure
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    
    # Dependencies
    python_requires=">=3.8",
    install_requires=[
        "ibapi>=9.81.1",
        "pandas>=1.3.0",
        "pytz>=2021.1",
        "python-dateutil>=2.8.2",
        "holidays>=0.13",
    ],
    
    # Classifiers
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
)
