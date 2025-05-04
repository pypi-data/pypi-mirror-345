from setuptools import setup, find_packages

setup(
    name='multasker',
    version='0.3.2',
    packages=find_packages(),
    install_requires=[],  # List any external dependencies here
    author='kalanik0a',
    author_email='seanjklum@gmail.com',
    description='A package for managing multiprocessing and multithreading tasks',
    url='https://github.com/kalanik0a/multasker',  # Replace with your repository URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
