from setuptools import setup, find_namespace_packages

setup(
    name='brynq_sdk_jira',
    version='2.1.1',
    description='JIRA wrapper from BrynQ',
    long_description='JIRA wrapper from BrynQ',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=find_namespace_packages(include=['brynq_sdk*']),
    license='BrynQ License',
    install_requires=[
        'brynq-sdk-brynq>=2',
        'pandas>=1,<3',
        'requests>=2,<=3'
    ],
    zip_safe=False,
)