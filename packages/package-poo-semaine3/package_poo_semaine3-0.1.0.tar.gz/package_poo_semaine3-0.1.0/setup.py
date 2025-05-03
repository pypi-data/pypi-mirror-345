from setuptools import setup, find_packages

setup(
  name="package_poo_semaine3",
  version="0.1.0",
  description="exemple de package typique avec python",
  long_description=open("README.md").read(),
  author="courses",
  author_email="courses@python.py",
  url="https://github.com/username/mon_package",

  packages=find_packages(),
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  python_require=">=3.6",
  install_requires=[
    "numpy>=1.18.0",
    "pandas>=1.0.0"
  ],

)