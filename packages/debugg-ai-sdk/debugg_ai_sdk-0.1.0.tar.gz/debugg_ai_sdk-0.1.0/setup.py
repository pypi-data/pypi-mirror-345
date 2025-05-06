from setuptools import setup, find_packages

setup(
    name="debugg-ai-sdk",
    version="0.1.0",
    description="Debugg AI's official Python sdk for connecting your personal AI QA engineer",
    author="Debugg AI Team",
    author_email="support@debugg.ai",
    url="https://github.com/debugg-ai/debugg-ai-python",
    project_urls={
        "Documentation": "https://docs.debugg.ai/platforms/python"
    },
    packages=find_packages(),
    install_requires=[],  # If you have any dependencies, list them here
    tests_require=["pytest"],  # If you're using pytest
    test_suite="tests",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
