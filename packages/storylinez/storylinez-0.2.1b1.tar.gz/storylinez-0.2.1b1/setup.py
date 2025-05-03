from setuptools import setup, find_packages
from pathlib import Path

# Get the long description from the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='storylinez',
    version='0.2.1b1',  # Incremented patch version for bugfixes
    license="MIT",
    author='Sayanti Chatterjee, Ranit Bhowmick',
    author_email='sayantichatterjee28@gmail.com, bhowmickranitking@gmail.com',
    description='Storylinez: A modular library for narrative generation and story manipulation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages('src', include=["storylinez", "storylinez.*"]),
    package_dir={'': 'src'},
    url='https://github.com/Kawai-Senpai/Storylinez-SDK',
    install_requires=[
        'python-dotenv',
        'ultraprint>=3.3.0',
    ],
    python_requires='>=3.6',
)
