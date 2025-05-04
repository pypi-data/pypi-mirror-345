from __future__ import print_function
from glob import glob
from setuptools import setup,Extension
import os
import re
from pathlib import Path

def get_version():
    version = "0.4.1-2"
    if 'GITHUB_REF' in os.environ:
        github_ref = os.environ['GITHUB_REF']
        match = re.match(r'refs/tags/v(.*)', github_ref)
        if match:
            version = match.group(1)
    return version

sources = ['curve25519module.c', 'curve/curve25519-donna.c']
sources.extend(glob("curve/ed25519/*.c"))
sources.extend(glob("curve/ed25519/additions/*.c"))
sources.extend(glob("curve/ed25519/nacl_sha512/*.c"))
#headers = ['curve25519-donna.h']
module_curve = Extension('pywaves_curve25519',
                    sources = sorted(sources),
#                   headers = headers,
                    include_dirs = [
                      'curve/ed25519/nacl_includes',
                      'curve/ed25519/additions',
                      'curve/ed25519'
                      ]
                    )
setup(
    name='PyWaves-Curve25519',
    version=get_version(),
    license='GPL-3.0',
    author='Tarek Galal',
    ext_modules = [module_curve],
    author_email='tare2.galal@gmail.com',
    description='Curve25519 (Ed25519 sign/verify with X25519 keys) for Waves blockchain',
    long_description=Path(__file__).with_name("README.md").read_text(encoding="utf-8"),
    long_description_content_type='text/markdown',
    url='https://github.com/PyWaves-CE/PyWaves-Curve25519',
    python_requires='>=3.8',
    keywords='cryptography curve25519 ed25519 x25519 pywaves waves blockchain',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Security :: Cryptography',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/PyWaves-CE/PyWaves-Curve25519/issues',
        'Source': 'https://github.com/PyWaves-CE/PyWaves-Curve25519',
    },
    platforms='any'
)
