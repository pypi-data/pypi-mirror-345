# -*- coding: utf-8 -*-

# Note to self: To upload a new version to PyPI, run:
# python setup.py sdist upload

from setuptools import setup, find_packages

setup(
    name='xml_diff',
    version='0.7.1',
    author=u'Joshua Tauberer',
    author_email=u'jt@occams.info',
    packages = find_packages(),
    url='https://github.com/joshdata/xml_diff',
    license='Unlicense',
    description='Compares two XML documents by diffing their text, ignoring structure, and wraps changed text in <del>/<ins> tags.',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords = "compare diff XML",
    install_requires=["lxml"],
)
