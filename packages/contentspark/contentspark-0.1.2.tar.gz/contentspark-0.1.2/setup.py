from setuptools import setup, find_packages

setup(
    name='contentspark',  
    version='0.1.2',      
    packages=find_packages(),
    install_requires=[
        'google-cloud-discoveryengine',
        'google-api-core'
    ],
    author='Karthik Sunil K',
    author_email='karthiksunil.me@gmail.com',
    description='Fetch responses from GCP Discovery Engine (Agent Builder Chat App)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Karthik-Sunil-K/contentspark',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)
