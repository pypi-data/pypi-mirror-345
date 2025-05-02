from setuptools import setup

setup(
    name='JsonDot',
    version='0.2',
    description='Load JSON files and use the data with dot notation then dump to the file',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Mits-Soft/JsonDot.git',
    author='Marco Antonio Calviño Coira',
    author_email='mits.soft.main@gmail.com',
    license='MIT',
    packages=['jsondot'],
    classifiers=[
        'Development Status :: 3 - Alpha',        
        'License :: OSI Approved :: MIT License',       
        'Programming Language :: Python :: 3.12'
    ],
)