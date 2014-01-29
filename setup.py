from distutils.core import setup
import xmlformatter

setup(
    name = 'xmlformatter',
    version = xmlformatter.__version__,
    author = 'P. Andreas Moeller',
    author_email = 'kontakt@pamoller.com',
    url = 'http://pamoller.com/xmlformatter.html',
    license = 'MIT',
    description = 'Format and compress XML documents',
    long_description = open('README.rst', 'r').read(),
    py_modules = ['xmlformatter'],
    scripts = ['bin/xmlformat'],
    classifiers = [
     "Programming Language :: Python :: 2",
     "Programming Language :: Python :: 2.6",
     "Programming Language :: Python :: 2.7",
     "Programming Language :: Python :: 3",
     "Programming Language :: Python :: 3.2",
     "License :: OSI Approved :: MIT License",
     "Topic :: Text Processing :: Markup :: XML"
    ]
)
