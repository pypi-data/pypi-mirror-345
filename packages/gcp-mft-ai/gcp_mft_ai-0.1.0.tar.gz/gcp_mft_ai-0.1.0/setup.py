# setup.py

from setuptools import setup, find_packages

setup(
    name="gcp-mft-ai",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-enhanced Managed File Transfer for Google Cloud (GCS, Filestore, Storage Transfer Service)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourgithub/gcp-mft-ai",
    packages=find_packages(),
    install_requires=[
        "google-cloud-storage",
        "cryptography",
        "scikit-learn",
        "pandas",
        "pyyaml",
        "requests",
        "joblib"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.7',
)
