from setuptools import find_packages
from setuptools import setup

version = '0.0'
requires = [
    'pyzmq', 
    'geventutil', 
    'pyramid', 
    #'ZMQTxn',  
    'path.py'
    ]

setup(name='ziggurat',
      version=version,
      description="Pyramid for async, non-http networking",
      long_description=open("README.rst").read(),
      classifiers=[], 
      keywords='pyramid networking zeromq gevent fapp fapp fapp',
      author='whitmo',
      author_email='whit at surveymonkey.com',
      url='http://ziggurat.github.com',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      entry_points="""
      [paste.server_factory]
      gpds=zig.service:GPasteDeployService
      [console_scripts]
      gpserve = zig.greenpserve:gpserve
      """,
      )
