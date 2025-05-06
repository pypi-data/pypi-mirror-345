from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()


setup(
    name="momoya",
    version="1.1.0",
    description="A package for extracting AI-generated images and videos from various platforms",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="deidax",
    author_email="deidaxtech@gmail.com",
    url="https://github.com/deidax/momoya",
    packages=find_packages(include=['momoya', 'momoya.*']),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'momoya=momoya.cli:main',
        ],
    },
    install_requires=[
        "aiohttp==3.8.0",
        "aiofiles==0.8.0",
        "pyfiglet==0.8.post1",
        "termcolor==1.1.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
    keywords='Scraping, AI, Images, Videos',
    license='MIT',
    # Explicitly ensure the package modules are included
    package_data={
        'momoya': ['*.py'],
        'momoya.core': ['*.py'],
        'momoya.extractors': ['*.py'],
    },
    # Make sure we aren't excluding any files
    zip_safe=False,
)