from setuptools import setup, find_namespace_packages

setup(
    name='brynq_sdk_elastic',
    version='3.0.4',
    description='elastic wrapper from BrynQ',
    long_description='elastic wrapper from BrynQ',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=find_namespace_packages(include=['brynq_sdk*']),
    license='BrynQ License',
    install_requires=[
        'requests>=2,<=3',
        'paramiko>=2,<=3'
    ],
    zip_safe=False,
)
