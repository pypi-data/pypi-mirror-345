from setuptools import setup

with open("README.md","r") as f:
    data = f.read()

setup(
    name='tuilib',  # Your library name
    version='4.1.0.0',  # Initial version
    description='A Python library for creating Terminal User Interfaces using curses',
    long_description=data,
    long_description_content_type="text/markdown",
    author='',
    author_email='umyashinderu@gmail.com',
    url='https://github.com/replit-user/tuilib',  # Link to your GitHub repository
    py_modules=['tuilib','windows-curses'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)