from __future__ import print_function
from glob import glob
from setuptools import setup,Extension
import os
import re

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
    license='GPLv3 License',
    author='Tarek Galal',
    ext_modules = [module_curve],
    author_email='tare2.galal@gmail.com',
    description='curve25519 with ed25519 signatures, used by PyWaves',
    platforms='any'
)
