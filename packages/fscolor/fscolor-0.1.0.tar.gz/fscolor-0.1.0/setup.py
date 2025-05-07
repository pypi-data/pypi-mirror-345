from setuptools import setup, find_packages
import io

# Fix encoding issues for Windows systems
def read_file(filename):
    with io.open(filename, encoding='utf-8') as f:
        return f.read()

setup(
    name="fscolor",
    version="0.1.0",
    author="Yusuf Muhammed Adekunle",
    author_email="muadeyus@gmail.com",
    description="Color formatting for f-strings",
    long_description=read_file('README.md'),
    long_description_content_type="text/markdown",
    url="https://github.com/Kunlex58/fscolor",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)