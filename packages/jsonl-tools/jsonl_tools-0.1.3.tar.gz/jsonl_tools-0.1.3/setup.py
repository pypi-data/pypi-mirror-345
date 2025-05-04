from setuptools import setup, find_packages

setup(
    name='jsonl_tools',
    version='0.1.3',
    description='A Python library for working with JSONL files',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='vladimirkucin634',
    author_email='vladimirkucin634@gmail.com',
    url='https://github.com/vladimirkucin634/jsonl_tools',
    packages=find_packages(),
    install_requires=[],  
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11"
    ],
    python_requires='>=3.7',
)
