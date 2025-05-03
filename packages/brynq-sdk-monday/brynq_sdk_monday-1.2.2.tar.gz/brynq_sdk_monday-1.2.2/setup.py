from setuptools import setup, find_namespace_packages

setup(
    name='brynq_sdk_monday',
    version='1.2.2',
    description='Monday.com wrapper from BrynQ',
    long_description='Monday.com wrapper from BrynQ',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=find_namespace_packages(include=['brynq_sdk*']),
    license='BrynQ License',
    install_requires=[
        'brynq-sdk-brynq>=2',
    ],
    zip_safe=False,
)
