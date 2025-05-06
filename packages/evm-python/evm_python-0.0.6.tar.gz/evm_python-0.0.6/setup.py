from setuptools import setup, find_packages

setup(
    name="evm_python",
    version="0.0.6",
    author="zefzhou44",
    author_email="zefzhou44@gmail.com",
    description="evm python package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/zefzhou/evm_py",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8.0",
    install_requires=[
        "bip44==0.1.5",
        "eth_typing>=5.2.1",
        "eth_utils>=5.3.0",
        "loguru>=0.7.2",
        "Requests>=2.32.3",
        "web3>=7.11.0",
    ],
)
