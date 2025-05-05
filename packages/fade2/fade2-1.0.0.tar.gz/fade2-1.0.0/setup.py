from setuptools import setup, find_packages

classifiers = [
  "Development Status :: 4 - Beta",
  "Intended Audience :: Developers",
  "Operating System :: OS Independent",
  "License :: OSI Approved :: MIT License",
  "Programming Language :: Python :: 3.10",
  "Topic :: Terminals"
]

setup(
  name="fade2",
  version="1.0.0",
  description="A sequence to venaxyt's fade project, with more features.",
  long_description=open("README.md", encoding="utf-8").read(),
  long_description_content_type="text/markdown",
  url="https://github.com/qrexpy/fade2",  
  author="Qrexxed",
  license="MIT",
  classifiers=classifiers,
  keywords="fade ascii art color gradient",
  packages=find_packages(),
  install_requires=[],
)