from setuptools import setup, find_packages

setup(
    name="mkdocs-auto-figure-list",
    version="0.1",
    description="auto creation for figures",
    author = "privatacc",
    packages=find_packages(),
    install_requires=[
        "mkdocs"
        ],
    entry_points={
        'mkdocs.plugins': [
            'auto-figure-list = plugin.plugin:FigureListCreation'
        ]
    }
)