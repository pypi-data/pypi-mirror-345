from setuptools import setup, find_packages

setup(
    name='python-test-aviz',
    version='0.1.0',
    packages=find_packages(include=['python_test_aviz', 'python_test_aviz.*']),
    install_requires=[
        'setuptools>=42.0.0',
        'wheel>=0.36.2',
        'custom-python-logger>=0.1.4',
    ],
    author='Avi Zaguri',
    author_email='',
    description='A test repository for testing the publishing process of a Python package.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/aviz92/python-test-aviz',
    project_urls={
        'Repository': 'https://github.com/aviz92/python-test-aviz',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
