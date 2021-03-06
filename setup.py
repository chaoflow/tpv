import os
import sys

from setuptools import setup, find_packages

version = '0.4.dev0'
shortdesc = 'Core of the vortex.'

#longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

install_requires = [
    'setuptools',
    'metachao',
]

if sys.version_info[0] is 2 and sys.version_info[1] < 7:
    install_requires.append('ordereddict')
    install_requires.append('unittest2')

setup(name='tpv',
      version=version,
      description=shortdesc,
      #long_description=longdesc,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development',
      ],
      keywords='',
      author='Florian Friesdorf',
      author_email='flo@chaoflow.net',
      url='http://github.com/chaoflow/tpv.core',
      license='AGPLv3+',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['tpv'],
      include_package_data=True,
      zip_safe=True,
      install_requires=install_requires,
      entry_points={
          'tpv.tests.eps': [
              'a = tpv.tests.test_tree_from_entry_points:A',
              'a/a = tpv.tests.test_tree_from_entry_points:AA',
              'a/b = tpv.tests.test_tree_from_entry_points:AB',
              'b = tpv.tests.test_tree_from_entry_points:B',
          ]
      })
