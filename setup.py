from setuptools import setup, find_packages

setup(name = "tatt",
      version = "0.1",
      packages = find_packages(),
      scripts = ['tatt'],

      install_requires = [''],

      # metadata for upload to PyPI
      author = "Thomas Kahle",
      author_email = "tom111@gmx.de",
      description = "tatt is an arch testing tool",
      license = "GPL-2",
      keywords = "gentoo arch testing",
      url = "http://github.com/tom111/tatt",   # project home page
      )
