from setuptools import setup, find_packages

setup(
    name='NumWord',
    version='0.0.5',
    packages=find_packages(),
    install_requires=[],
    author='Harshit Dalal',
    author_email='harshitdalal96@gmail.com',
    description='A package to convert words to numbers',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/HarshitDalal/NumWord',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    keywords=[
        'number', 'word', 'conversion', 'numbers2words',
        'number to word', 'word to number', 'num2words', 'words2number', 'numword'
    ],
    python_requires='>=3.6',
)
