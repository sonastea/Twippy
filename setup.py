from setuptools import setup

setup(
    name="Twippy",
    description="Discord bot providing updates by scraping Twitter",
    version="0.1.0",
    author="sonastea",
    license="MIT",
    packages=["twippy"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Discord :: Twitter :: Bot",
    ],
    install_requires=[
        "discord.py",
        "snscrape@git+https://github.com/JustAnotherArchivist/snscrape.git",
    ],
    python_requires=">=3.8",
    extras_require={"linters": ["pylint", "flake8", "pre-commit"]},
)
