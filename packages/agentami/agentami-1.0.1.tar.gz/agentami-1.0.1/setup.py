from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='agentami',
    version='1.0.1',
    packages=find_packages(exclude=["tests*", "examples*", ".venv*"]),
    install_requires=[
        "langchain>=0.3.24",
        "langchain-core>=0.3.56",
        "langchain-openai>=0.3.14",
        "langgraph>=0.3.34",
        "langgraph-checkpoint>=2.0.25",
        "langgraph-sdk>=0.1.63",
        "openai>=1.76.0",
        "tiktoken>=0.9.0",
        "faiss-cpu>=1.11.0",
        "sentence-transformers>=4.1.0",
        "scikit-learn>=1.6.1",
        "pydantic>=2.11.3",
        "python-dotenv>=1.1.0",
        "requests>=2.32.3",
        "orjson>=3.10.16",
        "rich>=14.0.0"
    ],
    author='Amish Gupta',
    author_email='amishgupta@outlook.com',
    description='Create an agent that can handle a large number of tools with persistence support.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ami-sh/agentami',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # You can change license type if needed
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    include_package_data=True,  # Useful if you add a MANIFEST.in later
)
