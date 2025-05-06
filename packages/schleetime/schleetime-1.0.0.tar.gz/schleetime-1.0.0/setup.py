from setuptools import setup

setup(
    name='schleetime',
    version='1.0.0',
    author='Gabe Schlee',
    author_email='schleeg@canisius.edu',
    py_modules=['timeserver'],
    install_requires=[
        'flask>=2.0.0'
    ],
    entry_points={
        'console_scripts': [
            'schleetime = timeserver:main',
        ],
    },
)

