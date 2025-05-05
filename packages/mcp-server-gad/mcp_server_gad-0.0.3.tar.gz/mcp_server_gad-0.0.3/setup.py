from setuptools import setup, find_packages

setup(
    name='mcp-server-gad',
    version='0.0.2',
    description='A secure MCP server that provides a read-only PostgreSQL query tool for gad.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Melody_Wu',
    author_email='Melody_Wu@compal.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'mcp>=1.7.1',
        'sqlalchemy',
        'psycopg2-binary'
    ],
    entry_points={
        'console_scripts': [
            'mcp-server-gad = mcp_server_gad.main:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
