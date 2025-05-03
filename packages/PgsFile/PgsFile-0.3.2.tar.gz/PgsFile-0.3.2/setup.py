# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 20:03:48 2023

@author: Petercusin
"""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PgsFile",
    version="0.3.2",
    author="Pan Guisheng",
    author_email="895284504@qq.com",
    description="This module simplifies Python package management, script execution, file handling, web scraping, and multimedia downloads. The module supports LLM-based NLP tasks such as tokenization, lemmatization, POS tagging, NER, dependency parsing, MDD, WSD, and MIP analysis. It also generates word lists and plots data, aiding literary students. Ideal for scraping data, cleaning text, and analyzing language, it offers user-friendly tools to streamline workflows.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://mp.weixin.qq.com/s/12-KVLfaPszoZkCxuRd-nQ?token=1589547443&lang=zh_CN",
    license="Educational free",
    install_requires=["chardet", "pandas", "python-docx", "pip", "requests", "fake-useragent", "lxml", "pimht", "pysbd", "nlpir-python","pillow"],
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Free For Educational Use",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)