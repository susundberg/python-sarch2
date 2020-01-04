
__author__  = 'Pauli Salmenrinne'

from setuptools import setup



requires = [
]

setup( name='sarch2',
      version="1.0.0",
      description='Simple archiving solution',
      
      scripts=['bin/sarch2'],
      packages=['sarch2'],
      
      long_description=open('README.rst').read(),
      url='https://github.com/susundberg/python-sarch2',
      author='Pauli Salmenrinne',
      author_email='susundberg@gmail.com',
      license='MIT',

      install_requires=requires,
      test_suite="test",
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Archiving',
        'Topic :: System :: Filesystems'
      ],
      zip_safe=True )
