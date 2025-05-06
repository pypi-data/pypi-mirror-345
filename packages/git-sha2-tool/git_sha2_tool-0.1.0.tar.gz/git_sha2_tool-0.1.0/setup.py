from setuptools import setup, find_packages

setup(
    name="git-sha2-tool",
    version="0.1",
    packages=find_packages(),
    install_requires=["requests"],
    entry_points={
        'console_scripts': [
            'git-sha2 = git_sha2.cli:main',
        ],
    },
    description="CLI to compute SHA-256 of files from Git URLs",
    author="Your Name",
)
