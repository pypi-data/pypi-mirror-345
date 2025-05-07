from setuptools import setup, find_packages

setup(
    name = 'an-huss-slodbo1',
    version='0.2',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts":[
            "an-sl = an:supervised_learning",
        ],
    },
    
)