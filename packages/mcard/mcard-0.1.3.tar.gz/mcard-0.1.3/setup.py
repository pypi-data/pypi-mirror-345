from setuptools import setup, find_packages
import os

# Read the content of README.md
with open(os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="mcard",
    version="0.1.1",
    packages=find_packages(include=['mcard', 'mcard.*']),
    description="MCard: Memory Card with TDD approach",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="MCard Team",
    author_email="user@example.com",  # Update with your email
    url="https://github.com/yourusername/MCard_TDD",  # Update with your repository URL
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    install_requires=[
        # Core dependencies
        "python-dateutil==2.8.2",
        "SQLAlchemy==1.4.47",
        "aiosqlite==0.17.0",
        "duckdb>=0.9.2",
        "lancedb>=0.3.3",
        "python-dotenv==1.0.0",
        

        
        # Logging and monitoring
        "structlog>=23.2.0",
        "python-json-logger==2.0.7",
    ],
    extras_require={
        "dev": [
            "pytest==7.4.3",
            "pytest-asyncio==0.23.2",
            "pytest-cov==4.1.0",
            "mypy>=1.7.1",
            "black>=23.11.0",
            "isort>=5.12.0",
        ],
    },
    python_requires=">=3.11.0",
    package_dir={"": "."},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "mcard=mcard.app.app:main",
        ],
    },
)