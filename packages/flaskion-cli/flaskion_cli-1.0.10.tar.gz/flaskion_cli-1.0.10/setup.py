from setuptools import setup, find_packages

setup(
    name="flaskion_cli",
    version="1.0.10",
    author="Graham Patrick",
    author_email="graham@skyaisoftware.com",
    description="A CLI tool for Flaskion — a lightweight MVC micro-framework built on Flask",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/GrahamMorbyDev/flaskion",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "flaskion_cli": [
            "flaskion_template/**/*",
            "cli_templates/**/*"
        ]
    },
    install_requires=[
        "click>=8.0",
        "jinja2>=3.0",
    ],
    entry_points={
    'console_scripts': [
        'flaskion=flaskion_cli.cli:cli',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)