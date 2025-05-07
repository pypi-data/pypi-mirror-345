from setuptools import setup, find_packages
import os
import re

# Read version from __init__.py
with open(os.path.join('drf_verbose_serializers', '__init__.py'), 'r') as f:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
    version = version_match.group(1)

# Read long description from README
with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='drf-verbose-serializers',
    version=version,
    author='Даниил Певзнер',
    author_email='pevzner.danil@gmail.com',
    description='Django REST framework extension providing verbose field names for serializers',
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/PevznerDanill/Django-Rest-Framework-Verbose-Serializers',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.7',
    install_requires=[
        'djangorestframework>=3.12.0',
    ],
    keywords='django, django-rest-framework, serializers, api',
) 