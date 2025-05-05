from setuptools import setup, find_packages

setup(
    name="git-push-cli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "groq",
    ],
    entry_points={
        "console_scripts": [
            "gitpush=gitpush.main:main",
        ],
    },
    author="Abdullah Bin Altaf",
    description="A natural-language Git CLI.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
