from setuptools import setup, find_packages

setup(
    name='ipars',
    version='3.1.1',
    description='Библиотека для работы с файлами во время парсинга',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author_email='statute-wasp-frisk@duck.com',
    packages=find_packages(),
    author='Ilia Miheev',
    license='MIT',
    install_requires=[
        'requests',
        'selenium',
        'lxml',
        'bs4',
    ],
)
