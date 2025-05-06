from setuptools import setup
from setuptools import find_packages

setup(
    name='gmctl',
    version='0.7.0',
    packages=find_packages(),
    install_requires=[
        'python-dotenv',
        'Click',
        'pydantic',
        'requests',
        'tabulate'
    ],
    entry_points={
        'console_scripts': [
            'gmctl = gmctl.gmctl:cli',
        ],
    },
)
