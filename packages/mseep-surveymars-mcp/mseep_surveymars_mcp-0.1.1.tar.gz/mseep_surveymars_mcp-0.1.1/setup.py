
from setuptools import setup, find_packages

setup(
    name="mseep-surveymars-mcp",
    version="0.1.1",
    description="SurveyMars MCP server",
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
    install_requires=['mcp>=1.6.0'],
    keywords=["mseep"] + ['SurveyMars', 'mcp', 'Survey'],
)
