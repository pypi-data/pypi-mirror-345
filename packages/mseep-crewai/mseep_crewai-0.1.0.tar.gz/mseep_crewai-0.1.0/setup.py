
from setuptools import setup, find_packages

setup(
    name="mseep-crewai",
    version="0.1.0",
    description="crewai using crewAI",
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
    install_requires=['crewai[tools]>=0.114.0,<1.0.0', 'fastapi>=0.95.0', 'uvicorn>=0.22.0', 'pydantic>=2.0.0'],
    keywords=["mseep"] + [],
)
