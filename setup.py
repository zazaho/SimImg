import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="simimg",
    version="0.8.1",
    author="Sacha Hony",
    author_email="zazahohonini@gmail.com",
    description="Similar Image Finder",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zazaho/SimImg",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
    install_requires=['Pillow'],
    entry_points={
        'console_scripts': ['simimg=simimg.simimg:main'],
        }
)
