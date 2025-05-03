from setuptools import find_packages
import file_dir_backup

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='file_dir_backup',
    version=file_dir_backup.__version__,
    description='A file and directory backup tool',
    # 详细说明（从README读取）
    long_description=long_description,
    long_description_content_type='text/markdown',
    license=file_dir_backup.__license__,
    author=file_dir_backup.__author__,
    author_email=file_dir_backup.__email__,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'file_dir_backup = file_dir_backup.cli:main'
        ]
    },
    install_requires=[],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: System :: Archiving :: Backup',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11'
    ],
    python_requires='>=3.6',
)
