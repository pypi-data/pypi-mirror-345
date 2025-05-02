from setuptools import setup, find_packages

VERSION = '2.5.0'


# Setting up
setup(
    name="pryvx",
    version=VERSION,
    author="PryvX (Jayesh Kenaudekar)",
    author_email="<jayesh@pryvx.com>",
    description="A comprehensive package for privacy-enhancing technologies",
    long_description_content_type="text/markdown",
    long_description=open('README.md').read(),
    packages=find_packages(),
    install_requires=[
        'grpcio',
        'grpcio-tools',
        'protobuf',
        'sympy',
        'numpy',
        'scikit-learn'
    ],
    keywords=['python', 
              'privacy-preserving', 
              'federated-learning', 
              'machine-learning', 
              'privacy-enhancing-technology', 
              'smpc', 
              'private-set-intersection'],

    classifiers=[
        'Programming Language :: Python :: 3.9',
        "Intended Audience :: Developers",
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    license='MIT',
    include_package_data=True,
)