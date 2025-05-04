import os
from setuptools import setup


def read(rel_path: str) -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path), 'r', encoding='UTF-8') as fp:
        return fp.read()


long_description = read("README.rst")

setup(
    name='sklearntools',
    packages=['sklearntools'],
    description="Tools of sklearn. Grid Search with multiprocess",
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='1.2.9',
    install_requires=[
        'numpy>=1.0.0',
        'scikit-learn>=0.20.0',
    ],
    url='https://gitee.com/summry/sklearntools',
    author='summy',
    author_email='xiazhongbiao@126.com',
    keywords=['sklearn', 'Grid Search', 'machine learning'],
    package_data={
        # include json and txt files
        '': ['*.rst', '*.dtd', '*.tpl'],
    },
    include_package_data=True,
    python_requires='>=3.6',
    zip_safe=False
)
