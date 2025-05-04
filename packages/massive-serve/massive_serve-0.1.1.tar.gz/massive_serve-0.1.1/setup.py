from setuptools import setup, find_packages

setup(
    name="massive_serve",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "click",  # Required for CLI
        "faiss-cpu",  # or faiss-gpu if you're using GPU
        "tqdm",
        "huggingface_hub",
        "flask",
        "flask-cors",
        "hydra-core",
        "omegaconf",
        "torch",
        "transformers",
        "sentence-transformers",
        "numpy",
    ],
    entry_points={
        'console_scripts': [
            'massive-serve=massive_serve.cli:cli',
        ],
    },
    author="Rulin Shao",
    author_email="rulins@cs.washington.edu",
    description="A package for massive serving",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/RulinShao/massive-serve",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
) 
