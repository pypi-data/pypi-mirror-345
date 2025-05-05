from setuptools import setup, find_packages


def readme():
  with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
  name='SdamMCKO',
  version='0.0.8',
  author='Fedor Tyulpin',
  author_email='f.tyulpin@gmail.com',
  description='A Python module for preparation for mcko',
  long_description=readme(),
  long_description_content_type='text/markdown',
  packages=find_packages(),
  install_requires=[],
  classifiers=[
    'Programming Language :: Python :: 3.13',
    'Operating System :: OS Independent'
  ],
  keywords='mcko',
  python_requires='>=3.6'
)