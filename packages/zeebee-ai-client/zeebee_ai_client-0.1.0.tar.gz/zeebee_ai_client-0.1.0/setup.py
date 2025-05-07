from setuptools import setup, find_packages

# Read the contents of the README file
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="zeebee-ai-client",
    version="0.1.0",
    description="Python SDK for the ZeebeeAI Chat Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ZeebeeAI Team",
    author_email="support@zeebee.ai",
    url="https://github.com/zeebeeai/zeebee-sdk-chat",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.25.0",
        "websockets>=10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.18.0",
            "mypy>=0.910",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=4.0.0",
            "twine>=4.0.0",
            "build>=0.8.0",
        ],
    },
    keywords=["ai", "chat", "sdk", "llm", "gpt", "claude", "voice", "zeebee"],
)
