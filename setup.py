from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()


VERSION = '0.4'
DESCRIPTION = 'pyRevizto is a library designed specifically for Python developers who work with Revizto, a popular platform for BIM collaboration and issue tracking. By leveraging pyRevizto, developers can streamline their workflows and significantly enhance the capabilities of Revizto through automation.'

# Setting up
setup(
    name="pyRevizto",
    version=VERSION,
    author="Umar Khalid",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['requests>=2.28.2', 
                      'python-dotenv>=1.0.1'],
    keywords=['Revizto'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.6',
    url="https://github.com/umarkhalid007/pyRevizto",
    project_urls={
        "Bug Tracker": "https://github.com/umarkhalid007/pyRevizto/issues",
    },
)