import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent
README = (HERE / 'README.md').read_text()


def read_requirements(reqs_path):
    with open(reqs_path, encoding='utf8') as f:
        reqs = [
            line.strip()
            for line in f
            if not line.strip().startswith('#') and not line.strip().startswith('--')
        ]
    return reqs


setup(
    name="indonesian_ie",
    version="0.0.1",
    description="indonesian_ie",
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/imvladikon/indonesian_nlp_play/',
    author='imvladikon@gmail.com',
    author_email='imvladikon@gmail.com',
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering',
    ],
    packages=find_packages(exclude=['tests*', 'scripts', 'utils']),
    include_package_data=True,
    install_requires=read_requirements(HERE / 'requirements.txt'),
)
