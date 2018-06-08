
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import setuptools

setuptools.setup(
    name='mr_pycolab',
    version='1.0',
    description='A Toy Montezuma\'s Revenge Environment written in pycolab.',
    url='https://github.com/wookayin/montezuma-pycolab/',
    author='Jongwook Choi',
    author_email='wookayin@gmail.com',
    license='Apache 2.0',
    install_requires=[
        'numpy>=1.9',
        'pycolab>=1.0',
        'six',
    ],

    packages=['mr_pycolab'],
    zip_safe=True,
)
