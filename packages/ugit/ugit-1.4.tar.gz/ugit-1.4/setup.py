from setuptools import setup

setup(
    name='ugit',
    version='1.4',
    packages=['ugit_module'],
    entry_points={
        'console_scripts': [
            'ugit = ugit_module.cli:main',
            'ugit-gui = ugit_module.gui_launcher:main'
        ]
    }
)
