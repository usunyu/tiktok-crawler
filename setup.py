#!/usr/bin/python
"""Upload videos to Youtube."""
from distutils.core import setup

setup_kwargs = {
    "name": "tiktok-crawler",
    "version": "0.1.0",
    "description": "Fetch video list according challenge and user from Tik Tok",
    "author": "Yu Sun",
    "author_email": "usunyu@gmail.com",
    "url": "https://github.com/usunyu/tiktok-crawler",
    "packages": ["tiktok_crawler/"],
    "scripts": ["bin/tiktok-crawler"],
    "license": "MIT License",
    "long_description": " ".join(__doc__.strip().splitlines()),
    "classifiers": [
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    "entry_points": {
        'console_scripts': [
            'tiktok-crawler = tiktok_crawler.main:run'
        ],
    },
    "install_requires":[
        'requests',
        'PySocks',
        'urllib3'
    ],
}

setup(**setup_kwargs)
