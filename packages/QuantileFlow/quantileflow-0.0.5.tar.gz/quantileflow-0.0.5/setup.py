import os
import re
import setuptools

NAME             = "QuantileFlow"
AUTHOR           = "Dhyey Mavani"
AUTHOR_EMAIL     = "ddmavani2003@gmail.com"
DESCRIPTION      = "This package provides API and functionality to efficiently compute quantiles for anomaly detection in service/system logs. Developed under LogFlow-AI initiative."
LICENSE          = "Apache"
KEYWORDS         = "QuantileFlow"
URL              = "https://github.com/LogFlow-AI/" + NAME
README           = ".github/README.md"
CLASSIFIERS      = [
  "Programming Language :: Python",
]
INSTALL_REQUIRES = [
  "numpy",
  "pandas",
  "pytest",
  "coverage",
  "scipy",
  "matplotlib",
]
ENTRY_POINTS = {
  
}
SCRIPTS = [
  
]

HERE = os.path.dirname(__file__)

def read(file):
  with open(os.path.join(HERE, file), "r") as fh:
    return fh.read()

VERSION = re.search(
  r'__version__ = [\'"]([^\'"]*)[\'"]',
  read(NAME.replace("-", "_") + "/__init__.py")
).group(1)

LONG_DESCRIPTION = read(README)

if __name__ == "__main__":
  setuptools.setup(
    name=NAME,
    version=VERSION,
    packages=setuptools.find_packages(),
    author=AUTHOR,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license=LICENSE,
    keywords=KEYWORDS,
    url=URL,
    classifiers=CLASSIFIERS,
    install_requires=INSTALL_REQUIRES,
    entry_points=ENTRY_POINTS,
    scripts=SCRIPTS,
    include_package_data=True    
  )
