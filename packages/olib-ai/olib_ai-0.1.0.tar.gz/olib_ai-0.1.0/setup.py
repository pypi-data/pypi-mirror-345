from setuptools import setup, find_packages

setup(
    name="olib-ai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    author="Olib AI",
    author_email="akram@olib.ai",
    description="Olib AI - Python SDK (Coming Soon)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Olib-AI/olib-ai-python",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
    ],
    python_requires=">=3.12",
)
