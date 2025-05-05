from setuptools import setup, find_packages
from conippets import __version__

setup(
    name = 'conippets',
    packages = find_packages(exclude=['examples']),
    version = __version__,
    license='MIT',
    description = 'conippets',
    author = 'JiauZhang',
    author_email = 'jiauzhang@163.com',
    url = 'https://github.com/JiauZhang/conippets',
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type = 'text/markdown',
    keywords = [
    ],
    extras_require={
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
    ],
    python_requires=">=3.8",
)