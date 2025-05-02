from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='altastata',
    version='0.1.0',
    author='Serge Vilvovsky',
    author_email='serge.vilvovsky@altastata.com',
    description='A Python package for Altastata data processing and machine learning integration',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/sergevil/altastata-python-package',
    packages=find_packages(exclude=['altastata.lib']),  # Exclude lib directory
    include_package_data=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'py4j==0.10.9.5',
    ],
)

