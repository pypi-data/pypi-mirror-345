from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    readme = f.read()

setup(
    name='stax_ai_module_sdk',
    version='0.1.10',
    url='https://bitbucket.org/staxai/stax-module-sdk-py',
    author='Stax.ai, Inc. <https://stax.ai>',
    author_email='naru@stax.ai',
    description='Stax.ai Module SDK',
    long_description=readme,
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    license='CC-BY-NC 4.0',
    license_files=('LICENSE',), 
    python_requires='>=3.6',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=['retry_requests'],
    scripts=['bin/stax_module_cli']
)