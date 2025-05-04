from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
here_qualys_etl = pathlib.Path(here, "qualys_etl")
long_description = (here_qualys_etl / 'README.md').read_text(encoding='utf-8')

setup(
    name='qualysetl',
    version='0.9.9',
    packages=find_packages(include=['qualys_etl', 'qualys_etl.*']),
    scripts=['bin/qetl_setup_python_venv'],
    url='https://pypi.org/project/qualysetl/',
    project_urls={
        'Documentation': 'https://dg-cafe.github.io/qualysetl/',
        'Qualys Video Series': 'https://blog.qualys.com/tag/api-best-practices-series',
    },
    keywords='qualys, etl, qualys.com, david gregory, qualysetl, qualysapi',
    license='Apache',
    author='David Gregory',
    author_email='dgregory@qualys.com, dave@davidgregory.com',
    description='Qualys API Best Practices Series - ETL Blueprint Example Code within Python Virtual Environment',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: POSIX :: Linux',
    ],
    python_requires='>=3.8.5',
    package_data={'': ['*.yaml', '.*.yaml', '*.sh', '*.md']},
)
