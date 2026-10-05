"""
Setup script for SubFluxGPT
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

setup(
    name='subfluxgpt',
    version='1.0.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='Next-generation AI-powered subdomain enumeration for bug bounty hunters',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/SubFluxGPT',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Topic :: Security',
        'Topic :: System :: Networking',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
    install_requires=[
        'google-generativeai>=0.3.0',
        'anthropic>=0.18.0',
        'openai>=1.0.0',
        'aiohttp>=3.9.0',
        'httpx>=0.25.0',
        'dnspython>=2.4.0',
        'tldextract>=5.0.0',
        'python-dotenv>=1.0.0',
    ],
    entry_points={
        'console_scripts': [
            'subfluxgpt=subfluxgpt.cli:cli_entry',
        ],
    },
    keywords='subdomain enumeration bug bounty security reconnaissance ai gemini claude netlas bbrf',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/SubFluxGPT/issues',
        'Source': 'https://github.com/yourusername/SubFluxGPT',
        'Documentation': 'https://github.com/yourusername/SubFluxGPT/blob/main/README.md',
    },
)
