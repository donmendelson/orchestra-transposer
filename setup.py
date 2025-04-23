from setuptools import setup

setup(
    name='orchestra-transposer',
    version='0.0.2',
    packages=['tests', 'orchestratransposer', 'orchestratransposer.sbe', 'orchestratransposer.orchestra',
              'orchestratransposer.unified'],
    url='https://github.com/FIXTradingCommunity/orchestra-transposer',
    license='Apache 2.0',
    author='Donald Mendelson',
    author_email='donmendelson@gmail.com',
    description='Converts between FIX Orchestra and other formats'
)
