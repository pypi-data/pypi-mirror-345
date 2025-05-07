from setuptools import setup, find_namespace_packages

setup(
    name='brynq_sdk_salesforce',
    version='2.0.2',
    description='Salesforce wrapper from BrynQ',
    long_description='Salesforce wrapper from BrynQ',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=find_namespace_packages(include=['brynq_sdk*']),
    license='BrynQ License',
    install_requires=[
        'brynq-sdk-brynq>=2',
        'requests>=2,<=3',
        'pandas>=1,<3',
        'pyarrow>=10'
    ],
    zip_safe=False,
)