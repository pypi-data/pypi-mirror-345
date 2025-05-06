from setuptools import setup, find_packages

setup(
    name='nlb-lottery',
    version='0.0.1',
    packages=find_packages(),
    install_requires=['requests'],
    author='Ishan Oshada',
    author_email='ishan.kodithuwakku.official@email.com',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    description='under development',
    url='https://github.com/ishanoshada/nlb-lottery',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
