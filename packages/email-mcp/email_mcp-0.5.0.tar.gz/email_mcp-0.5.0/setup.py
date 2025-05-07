from setuptools import setup, find_packages

setup(
    name="email-mcp",
    version="0.5.0",
    packages=find_packages(),
    install_requires=[
        "mcp",
    ],
    entry_points={
        'console_scripts': [
            'email-mcp=email_mcp.server:main',
        ],
    },
    author="Hadi Azarabad",
    author_email="mhazarabad@gmail.com",
    description="An MCP server for sending and searching emails",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mhazarabad/email-mcp",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
) 