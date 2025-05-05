from setuptools import setup, find_packages

setup(
    name="sqlproxy",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "keyboard",
        "urllib3"
    ],
    entry_points={
        'console_scripts': [
            'sqlproxy=sqlproxy.cli:main',
        ],
    },
    author="Your Name",
    description="A simple proxy automation tool using Burp Suite for login testing",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires='>=3.6',
)
