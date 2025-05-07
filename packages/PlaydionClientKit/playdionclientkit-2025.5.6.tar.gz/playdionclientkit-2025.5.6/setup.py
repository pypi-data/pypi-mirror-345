import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PlaydionClientKit",
    version="2025.5.6",
    author="Adrian Albrecht",
    author_email="adriandevprojects@gmail.com",
    packages=setuptools.find_packages(),
    url="https://github.com/AdrianDevProjects/ClientKit",
    license="GPL-3.0",
    description="ClientKit for Playdion Client",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
