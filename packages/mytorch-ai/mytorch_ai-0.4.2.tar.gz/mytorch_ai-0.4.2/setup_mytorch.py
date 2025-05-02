from setuptools import setup, find_packages

setup(
    name="mytorch-ai",
    version="0.4.2",
    description="Drop-in replacement for PyTorch that does distributed training and inference on a remote server",
    include_package_data=True,
    license="Custom License",
    long_description=open('README.md').read(),  # Note: path changed
    long_description_content_type='text/markdown',
    author="mytorch.net",
    author_email='pypi@mytorch.net',
    url="https://mytorch.net",
    classifiers=[
       "Development Status :: 4 - Beta",
       "Intended Audience :: Developers",
       "Intended Audience :: Science/Research",
       "Programming Language :: Python :: 3.10",
       "Topic :: Scientific/Engineering :: Artificial Intelligence",
       "License :: Other/Proprietary License",
    ],
    python_requires=">=3.10",
    install_requires=[
        "setuptools",
        "grpcio>=1.71.0",
        "grpcio-tools>=1.71.0",
        "numpy",
        "requests",
        "pillow",
        "tqdm",
        "matplotlib",
        "scikit-learn",
        "huggingface-hub"
    ],
    py_modules=["MyTorchClient"],
    packages=find_packages(
        include=[
            "torch*",
            "transformers*",
            "torchvision*",
            "proxies*", 
            "gRPC_impl*",
            "utils*",
            "connection_utils*",
        ],
        exclude=[
            "venv*",
            "venv.*",
            "*.venv*"
        ]
    ),
    package_data={
        '': ['LICENSE','README.md'],
        'torch': ['*.py'],
        'transformers': ['*.py'],
        'torchvision': ['*.py'],
        'proxies': ['*.py'],
        'gRPC_impl': ['*.py'],
        'utils': ['*.py'],
        'connection_utils': ['*.py'],
    },
) 
