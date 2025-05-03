
from setuptools import setup, find_packages

setup(
    name="mseep-20240407-test-mcp",
    version="0.1.0",
    description="Add your description here",
    author="mseep",
    author_email="support@skydeck.ai",
    url="",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=['fastapi[standard]>=0.115.12', 'httpx>=0.28.1', 'mcp[cli]>=1.6.0'],
    keywords=["mseep"] + [],
)
