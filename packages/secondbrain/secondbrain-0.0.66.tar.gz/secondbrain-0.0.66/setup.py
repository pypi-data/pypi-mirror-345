from setuptools import setup, find_packages

setup(
    name="secondbrain",
    version="0.0.66",
    packages=find_packages(),
    install_requires=[],
    author="Jie Xiong",
    author_email="363692146@qq.com",
    description="Package for secondbrain only!",
    long_description=open('README.md', encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    package_data={
        'secondbrain.bot': ['prompt.jinja'],
    },
)
