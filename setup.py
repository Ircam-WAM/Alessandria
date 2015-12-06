import re
import os
from setuptools import setup, find_packages


def read(*parts):
    return open(os.path.join(os.path.dirname(__file__), *parts)).read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    dir_to_exclude = ['__pycache__',]
    file_ext_to_exclude = ['.pyc', '.log',]
    file_pref_to_exclude = ['temp',]
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames) # Remove 1st occurence of 'alexandrie/' in dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        for d in dir_to_exclude:
            if base.find(d) >= 0:
                print(base, d)
                break
        else:
            for filename in filenames:
                if (os.path.splitext(filename)[1] not in file_ext_to_exclude and 
                    os.path.splitext(filename)[0] not in file_pref_to_exclude):
                    filepaths.append(os.path.join(base, filename))
    return {package: filepaths}

setup(
    name='django-alexandrie',
    version=find_version('alexandrie', '__init__.py'),
    description='Book library application for Django',
    author='Marc Schneider',
    author_email='marc@mirelsol.org',
    license="GPL v3",
    long_description="See README.rd",
    keywords="book library django application",
    url='https://gitlab.com/openlabmatera/alexandrie',
    packages=find_packages(),
    zip_safe=False,
    package_data=get_package_data('alexandrie'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
    ],
    install_requires=[
        'django>=1.7',
        'django-countries>=3.3',
        'django-ajax-selects>=1.3.6',
        'simplejson>=3.8.0',
        'pillow>=2.9.0',
        'isbnlib>=3.5.6'
    ]
)
