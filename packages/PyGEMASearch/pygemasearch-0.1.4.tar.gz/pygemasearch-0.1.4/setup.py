# setup.py
from setuptools import setup, find_packages

setup(
    name="PyGEMASearch",
    version="0.1.4",
    author="Mike Kremer",
    author_email="mikelsoft@gmail.com",
    description="A Python package to search for songs in the GEMA database.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/DonMikone/PyGEMASearch",
    packages=find_packages(),
    install_requires=[
        "requests"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'gemasearch=gemasearch.search:main'
        ]
    }
)
