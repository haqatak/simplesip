"""Setup script for simplesip package."""

from setuptools import setup, find_packages
import pathlib

# Get the long description from the README file
HERE = pathlib.Path(__file__).parent
long_description = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="simplesip",
    version="0.1.0",
    author="Awais Khan",
    author_email="contact@awaiskhan.com.pk",
    description="Simple SIP client library with RTP audio streaming capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Awaiskhan404/simplesip",
    packages=find_packages(exclude=["tests", "examples"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Communications :: Telephony",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.19.0",
    ],
    extras_require={
        "audio": ["pyaudio>=0.2.11"],
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "simplesip-demo=simplesip.examples.demo:main",
        ],
    },
    keywords="sip voip rtp audio streaming telephony simple",
    project_urls={
        "Bug Reports": "https://github.com/Awaiskhan404/simplesip/issues",
        "Source": "https://github.com/Awaiskhan404/simplesip",
        "Documentation": "https://simplesip.readthedocs.io/",
    },
)