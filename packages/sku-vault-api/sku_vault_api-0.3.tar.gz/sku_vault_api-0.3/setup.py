#!/usr/bin/env python

# Support setuptools only, distutils has a divergent and more annoying API and
# few folks will lack setuptools.
from setuptools import setup
# from importlib.resources import open_text
# Version info -- read without importing
_locals = {}

# PyYAML ships a split Python 2/3 codebase. Unfortunately, some pip versions
# attempt to interpret both halves of PyYAML, yielding SyntaxErrors. Thus, we
# exclude whichever appears inappropriate for the installing interpreter.
exclude = ["*.yaml2", 'test']

# Frankenstein long_description: version-specific changelog note + README
with open('README.md') as f:
    long_description = f.read()

extras = {}
all_extras = set()
for x in [ 'dev' ]:
    filename = f'{x}.txt'
    with open(filename, 'r') as f:
        st = f.read()
    rg = st.split()
    extras[x] = rg
    if x != 'dev':
        all_extras |= set(rg)
if all_extras:
    all_extras = list(all_extras)
    all_extras.sort()
    extras['all'] = all_extras


setup(
    name='sku_vault_api',
    version='0.3',
    description='sku_vault_api',
    license='BSD',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='dev',
    author_email='developers@directbuy.com',
    url='https://bitbucket.org/dbuy/sku_vault_api',
    packages=[
        'sku_vault_api',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'deceit',
        'pytz',
    ],
    extras_require=extras,
)