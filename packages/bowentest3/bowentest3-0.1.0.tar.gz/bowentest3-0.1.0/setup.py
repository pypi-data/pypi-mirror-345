from setuptools import setup, find_packages

setup(
    name="bowentest3",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'mcp>=1.7.0',
    ],
    entry_points={
        'console_scripts': [
            'mcp-server=bowentest3.server:main'
        ]
    },
    author="bowen",
    description="bowentest3",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    python_requires='>=3.10',
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License"
    ]
)
