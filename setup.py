from setuptools import setup, find_packages

setup(
    name                 = 'dgscored',
    version              = '0.1',
    long_description     = __doc__,
    packages             = find_packages(),
    include_package_data = True,
    zip_safe             = False,
    entry_points         = {
        'console_scripts': [
            'dgscored = dgscored.manage:main',
        ],
    },
)
