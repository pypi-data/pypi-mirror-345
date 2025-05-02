from setuptools import setup, find_packages

setup(
    name="endura-sdk",
    version="0.1.0",
    description="A trust layer SDK for Edge AI models",
    author="EnduraAI",
    author_email="hi@michaelkirschbaum.com",
    url="https://github.com/yourusername/endura-sdk",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "torch>=2.0",
        "psutil",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)