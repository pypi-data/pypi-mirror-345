from setuptools import setup, find_packages

setup(
    name="src-sdk",
    version="0.1.0",
    description="Trust layer SDK for Edge AI devices",
    author="Michael Kirschbaum",
    author_email="hi@michaelkirschbaum.com",
    url="https://github.com/yourusername/endura-sdk",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0",
        "psutil"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.7',
)