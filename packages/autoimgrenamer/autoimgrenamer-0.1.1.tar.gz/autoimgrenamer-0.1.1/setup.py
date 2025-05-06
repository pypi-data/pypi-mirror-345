from setuptools import setup, find_packages

setup(
    name='autoimgrenamer', 
    version='0.1.1',
    packages=find_packages(),
    install_requires=[],
    author='Md. Ismiel Hossen Abir',
    author_email='ismielabir1971@gmail.com',
    description='A simple tool to rename image files in a folder.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)