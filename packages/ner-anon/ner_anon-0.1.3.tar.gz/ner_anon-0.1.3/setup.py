from setuptools import setup, find_packages

setup(
    name='ner_anon',
    version='0.1.3',
    packages=find_packages(),
    install_requires=[
        'transformers>=4.0.0',
        'torch',  # You might want to pin a version
    ],
    author='Aimar_bp',
    description='A NER-based anonymization tool that replaces named entities in text with random entities from a given context.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)