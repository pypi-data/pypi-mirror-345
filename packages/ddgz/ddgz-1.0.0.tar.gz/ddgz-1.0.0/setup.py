import setuptools
import distutils.core

setuptools.setup(
    name='ddgz',
    version="1.0.0",
    author='talwrii',
    long_description_content_type='text/markdown',
    author_email='talwrii@gmail.com',
    description='Search with duckduckgo from the command-line, fuzzy select the results.',
    license='MIT',
    keywords='duckduckgo,search',
    url='https://github.com/talwrii/ddgz',
    install_requires=["ddgr", "python-fzf"],
    packages=["ddgz"],
    long_description=open('README.md').read(),
    entry_points={
        'console_scripts': ['ddgz=ddgz.main:main']
    },
)
