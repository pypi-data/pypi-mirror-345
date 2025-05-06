from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    
setup(
    name="link-nlp",
    version="0.4.3",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "transformers>=4.0.0",
        "torch>=2.0.0",
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "selenium>=4.0.0",
        "pymilvus>=2.0.0",
        "vllm>=0.1.0",
        "spacy>=3.0.0",
        "tqdm>=4.62.0",
        "accelerate>=0.20.0",
        # Dipendenze per spacy
        "cymem>=2.0.0",
        "preshed>=3.0.0",
        "murmurhash>=1.0.0",
        "thinc>=8.0.0",
        # Dipendenze per vllm
        "ninja>=1.10.0",
        "packaging>=21.0",
        "psutil>=5.8.0",
        "ray>=2.0.0",
        # Dipendenze per sentencepiece
        "protobuf>=3.20.0",
        "sentencepiece>=0.1.99",
    ],
    extras_require={
        "gliner": [
            "gliner>=0.1.0",  
        ],
        "transformers": [
            "transformers>=4.0.0",
            "torch>=2.0.0",
            "accelerate>=0.20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "link-ner=link_nlp.text_processing.ner_extractor:main",
        ],
    },
    python_requires=">=3.8",
    author="Lorenzo Molfetta",
    author_email="lorenzo.molfetta@unibo.it",
    description="Legal Information Knowledge with Natural Language Processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LorMolf/link",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Legal Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
) 