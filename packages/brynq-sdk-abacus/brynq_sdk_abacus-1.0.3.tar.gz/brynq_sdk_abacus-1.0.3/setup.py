from setuptools import setup, find_namespace_packages

setup(
    name='brynq_sdk_abacus',
    version='1.0.3',
    description='Abacus wrapper from BrynQ',
    long_description='Abacus wrapper from BrynQ',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=find_namespace_packages(include=['brynq_sdk*']),
    license='BrynQ License',
    install_requires=[
        'brynq-sdk-brynq>=2',
        'pandas>=2,<3'
    ],
    zip_safe=False,
)
