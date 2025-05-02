from setuptools import setup, find_packages

setup(
    name='AKSHATEDA',
    version='0.1.0',
    description='An interactive Python package for automated Exploratory Data Analysis (EDA)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your@email.com',
    url='https://github.com/yourusername/AKSHATEDA',  # if you have GitHub
    packages=find_packages(),
    install_requires=[
        'pandas', 'numpy', 'matplotlib'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
