import os
import sys
from setuptools import setup, find_namespace_packages
from fnmatch import fnmatchcase
from distutils.util import convert_path

standard_exclude = ('*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build', './dist', 'EGG-INFO', '*.egg-info')

def find_package_data(where='.', package='', exclude=standard_exclude, exclude_directories=standard_exclude_directories):
    out = {}
    stack = [(convert_path(where), '', package)]
    while stack:
        where, prefix, package = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                if os.path.isfile(os.path.join(fn, '__init__.py')):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + '.' + name
                        stack.append((fn, '', new_package))
                else:
                    stack.append((fn, prefix + name + '/', package))
            else:
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix+name)
    return out

setup(name='docassemble.KinshipConnector',
      version='1.1.1',
      description=('A docassemble extension to assist clients with educating themselves on the different types of kinship documents and create completed documents once chosen.'),
      long_description="Legal Aid of West Virginia's Kinship Connector.\r\n\r\nThis tool is designed to assist the general public with educating themselves on the different types of kinship arrangements available to them.  Once the user chooses a document to create, the interview will guide the user in entering the information needed to complete either a 1) Temporary Care Agreement, 2) Infant Guardianship, or 3) Adoption packet.  Once completed, these packets will provide instructions to the users on the next steps in their kinship process, including when and where to sign and how to print and submit to the court (if necessary).\r\n\r\nThis project was developed as part of a LSC TIG and made available for reproduction and modification pursuant to grant requirements.",
      long_description_content_type='text/markdown',
      author='Dane Henry, Esq.',
      author_email='dhenry@lawv.net',
      license='The MIT License (MIT)',
      url='https://docassemble.org',
      packages=find_namespace_packages(),
      install_requires=[],
      zip_safe=False,
      package_data=find_package_data(where='docassemble/KinshipConnector/', package='docassemble.KinshipConnector'),
     )

