import os
from distutils.core import setup

from reporter import VERSION
 
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
 
README = read('README.rst')
 
setup(
    name = 'django-reporter',
    version = '.'.join(map(str, VERSION)),
    url = 'http://github.com/pegasus/django-reporter',
    license = 'BSD',
    description = "Custom email-based reports for any Django project.",
    long_description = README,
    author = 'Brandon Konkle',
    author_email = 'brandon.konkle@gmail.com',
    packages = [
        'reporter',
        'reporter.management',
        'reporter.management.commands',
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
