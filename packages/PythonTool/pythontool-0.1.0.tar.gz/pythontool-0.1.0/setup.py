from setuptools import setup, find_packages

setup(
    name='PythonTool',
    version='0.1.0',
    author='Zhu Chongjing',
    author_email='tommy1008@dingtalk.com',
    description='A package for tools in Python',
    packages=find_packages(),
    install_requires=[
        'manim',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)