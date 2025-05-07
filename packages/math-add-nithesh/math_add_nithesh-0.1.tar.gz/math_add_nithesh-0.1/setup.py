from setuptools import setup, find_packages

setup(
    name='math-add-nithesh',            # Must be unique on PyPI
    version='0.1',
    packages=find_packages(),
    description='A simple math addition function',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Nithesh',
    author_email='your_email@example.com',
    url='https://github.com/yourusername/math-add-nithesh',  # Optional
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
)
