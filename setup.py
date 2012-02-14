from setuptools import find_packages
from setuptools import setup

version = '0.0'

setup(name='ziggurat',
      version=version,
      description="Pyramid for async, non-http networking",
      long_description=open("README.rst").read(),
      classifiers=[], 
      keywords='pyramid networking zeromq gevent fapp fapp fapp',
      author='whitmo',
      author_email='whit at surveymonkey.com',
      url='',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
