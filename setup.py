"""
Manage AWS REST API Gateway deployments
"""
from setuptools import find_packages, setup

from api_deploy import VERSION


def readme():
    with open('README.md') as f:
        return f.read()


dependencies = [
    'click>=8.1.3, <9',
    'mergedeep>=1.3.4',
    'boto3>=1.26.118',
    'PyYAML>=6.0',
    'requests>=2.31.0',
    'Jinja2==3.1.2',
    'urllib3<2',
]

setup(
    name='api-deploy',
    version=VERSION,
    url='https://github.com/fabfuel/api-deploy',
    download_url='https://github.com/fabfuel/api-deploy/archive/%s.tar.gz' % VERSION,
    license='BSD-3-Clause',
    author='Fabian Fuelling',
    author_email='pypi@fabfuel.de',
    description='Manage Amazon REST API Gateway deployments',
    long_description=readme(),
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            'api = api_deploy.cli:api',
        ],
    },
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
