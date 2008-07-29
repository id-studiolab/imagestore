from setuptools import setup, find_packages

setup(
    name='frontend',
    version='0.1',
    author='Martijn Faassen',
    author_email='faassen@startifact.com',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='BSD',
    install_requires=[
    'setuptools',
#    'Pygame >= 1.7.1',
    'lxml',
    ],
    entry_points= {
    'console_scripts': [
    'frontend = frontend.main:main',
    'filler = frontend.filler:main',
    ]
    },
)
