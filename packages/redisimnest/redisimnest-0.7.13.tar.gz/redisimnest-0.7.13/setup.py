from setuptools import setup, find_packages

setup(
    name='redisimnest',
    version='0.7.13',
    packages=find_packages(),
    install_requires=[
        'redis>=5.0', 
        'pytest>=8.3.5'
    ],
    description='A Redis key management system with dynamic prefixes and TTL support.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Ruhiddin Turdaliyev',
    author_email='niddihur@gmail.com',
    url='https://github.com/ruhiddin/redisimnest',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    license='MIT',
)


