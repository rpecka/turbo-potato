from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='turbo-potato',
      version=version,
      description="Compress videos to a specific file size on Windows so that they can be uploaded using the Discord free tier",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='discord video ffmpeg compression',
      author='Russell Pecka',
      author_email='russell@pecka.xyz',
      url='https://github.com/rpecka/turbo-potato',
      license='MIT',
      packages=['turbo_potato'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points={
            'console_scripts': [
                  'turbo-potato = turbo_potato:main',
            ]
      },
)
