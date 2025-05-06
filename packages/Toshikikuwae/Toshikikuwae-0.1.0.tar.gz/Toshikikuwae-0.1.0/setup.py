from setuptools import setup, find_packages

setup(
    name='Toshikikuwae',  # パッケージ名（PyPIで一意である必要あり）
    version='0.1.0',
    packages=find_packages(),
    description='A simple math library',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='you@example.com',
    #url='https://github.com/yourname/mylib',   任意（GitHubなど）
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
