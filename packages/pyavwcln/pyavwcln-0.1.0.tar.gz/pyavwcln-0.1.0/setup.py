from setuptools import setup, find_packages

setup(
    name='pyavwcln',
    version='0.1.0',
    author='Your Name',
    author_email='alessandro.vaccari@unife.it',
    description='A short description of your package',
    # long_description=open('README.md').read(),
    # long_description_content_type='text/markdown',
    # url='https://github.com/yourusername/your-lib-name',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)