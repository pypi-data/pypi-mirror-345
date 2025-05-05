from setuptools import setup, find_packages
 
setup(
    name="bowen_test_2",  # 包名，pip install 时用这个
    version="0.1.0",
    description="A simple hello tool",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="bowen",
    author_email="704836663@qq.com",
    url="",  # 可选：放 GitHub 仓库地址
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)