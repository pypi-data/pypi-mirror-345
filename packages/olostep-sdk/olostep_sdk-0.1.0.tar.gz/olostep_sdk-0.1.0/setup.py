from setuptools import setup, find_packages

setup(
    name='olostep-sdk',
    version='0.1.0',
    description='Official Python SDK for Olostep Web Scraping API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Mohammad Ehsan Ansari',
    author_email='you@example.com',
    url='https://github.com/yourusername/olostep-sdk',
    packages=find_packages(),
    install_requires=['requests'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7',
)