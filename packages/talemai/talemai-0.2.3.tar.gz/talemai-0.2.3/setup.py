from setuptools import setup, find_packages

setup(
    name='talemai',
    version='0.2.3',
    author='Hemit Patel',
    description='A description of your project',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.8',
    install_requires=[
        'click',
        'aiofiles',
        'PyPDF2',
        'pypdf',
        'pyfiglet',
        'langchain',
        'langchain-community',
        'langchain-astradb',
        'langchain-huggingface',
    ],
    entry_points={
        'console_scripts': [
            'talemai = talemai.__main__.py:main',  # Adjust path as needed
        ],
    },
)
