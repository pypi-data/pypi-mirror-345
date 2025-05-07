from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="browzy",  # Nama package harus 'browzy'
    version="0.1.0",
    author="QUHU",
    author_email="ferdisa321@gmail.com",
    description="A simple terminal-based web browser with Google search integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/QUHu-FER/browzy",
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'googlesearch-python',
        'colorama',
        'pyfiglet',
    ],
    entry_points={
        'console_scripts': [
            'browzy=browzy.core:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    keywords='browser terminal web-browser search google cli',
    python_requires=">=3.6",
)
