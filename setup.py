from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()


VERSION = '0.93'
DESCRIPTION = (
    'pyRevizto is a library designed specifically for Python developers who work with Revizto, '
    'a popular platform for BIM collaboration and issue tracking. By leveraging pyRevizto, '
    'developers can streamline their workflows and significantly enhance the capabilities of '
    'Revizto through automation.'
)

# Development and testing dependencies
DEV_REQUIRES = [
    'pytest>=7.0.0',
    'pytest-cov>=4.0.0',
    'black>=23.0.0',
    'flake8>=6.0.0',
    'isort>=5.12.0',
    'mypy>=1.0.0',
    'bandit>=1.7.5',
    'types-requests>=2.28.0',
    'types-python-dotenv>=1.0.0',
    'pre-commit>=3.0.0',
]

# Setting up
setup(
    name="pyrevizto",
    version=VERSION,
    author="Umar Khalid",
    author_email="umarkhalid007@gmail.com",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/umarkhalid007/pyRevizto",
    project_urls={
        "Bug Tracker": "https://github.com/umarkhalid007/pyRevizto/issues",
        "Documentation": "https://github.com/umarkhalid007/pyRevizto#readme",
        "Source Code": "https://github.com/umarkhalid007/pyRevizto",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.6",
    install_requires=[
        'requests>=2.28.2',
        'python-dotenv>=1.0.1',
    ],
    extras_require={
        'dev': DEV_REQUIRES,
    },
    keywords=['Revizto', 'BIM', 'Collaboration', 'API'],
    license="GPLv3",
)
