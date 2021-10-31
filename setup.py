from setuptools import setup, find_packages

setup(name = "tatt",
      version = "0.9",
      packages = find_packages(),
      scripts = ['scripts/tatt'],
      package_data = {
          'tatt': ['dot-tatt-spec']
          },

      install_requires = ['configobj>=4.6'],

      # metadata for upload to PyPI
      author = "Thomas Kahle",
      author_email = "tom111@gmx.de",
      description = "tatt is an arch testing tool",
      license = "GPL-2",
      keywords = "gentoo arch testing",
      url = "http://github.com/gentoo/tatt",   # project home page
      )
