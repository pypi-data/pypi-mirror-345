from setuptools import setup, find_packages
setup(
    name='libela',  # Replace with the desired package name
    version='0.0.3',
    packages=find_packages(),
    description='A brief description of your package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Arya Amiri',
    author_email='aryamiri@outlook.com',
    url='https://lib-ela.org',  # Optional
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Adjust the license type
        'Operating System :: OS Independent',
    ],
)
