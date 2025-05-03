from setuptools import setup

## setuptool config for pluginserver

setup(
    name='pluginserver',
    version='0.5.2',
    packages=['plugincore'],
    include_package_data=True,
    description='Plugin-driven API server',
    author='Your Name',
    url='https://github.com/nicciniamh/pluginserver',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'aiohttp',
	'aiohttp_cors',
    ],
    entry_points={
        'console_scripts': [
            'pserve = plugincore.pserv:main',
        ],
    },
)
