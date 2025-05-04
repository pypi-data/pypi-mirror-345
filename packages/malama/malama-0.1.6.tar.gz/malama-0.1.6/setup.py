from setuptools import setup, find_packages

setup(
    name='malama',
    version='0.1.6',
    packages=find_packages(),
    install_requires=[
        'pymupdf',
        'google-generativeai',
        'anthropic',
        'python-docx',
        'openpyxl'
    ],
    author='Manoj Prajapati',
    author_email='manojbittu161@gmail.com',
    description='Universal document assistant using popular AI models (PDF, Word, Excel)',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: General',
        'Topic :: Office/Business :: Office Suites',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.6',
)
