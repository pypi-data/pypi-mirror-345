from setuptools import setup, find_packages

setup(
    name='ts_features_sculptor',
    use_scm_version={
        'version_scheme': 'post-release',
        'local_scheme': 'node-and-date',
        'write_to': 'src/ts_features_sculptor/_version.py',
        'fallback_version': '1.0.0',
        'tag_regex': r'^v(\d+\.\d+\.\d+[^+]*)$',
    },
    description='A package for transforming time series features',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Nikolskii D.N.',
    author_email='nikolskydn@mail.ru',
    url='https://github.com/nikolskydn/ts_features_sculptor',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'pandas>=2.2.3',
        'scikit-learn>=1.5.1',
        'holidays>=0.31',
        'numpy>=1.24.0',
    ],
    setup_requires=[
        'setuptools_scm>=8.0.0',
        'wheel',
    ],
    tests_require=[
        'pytest>=7.4.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'build>=1.0.3',
            'twine>=4.0.2',
            'black>=23.12.0',
            'isort>=5.13.2',
            'flake8>=6.1.0',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
    include_package_data=True,
    zip_safe=False,
    license_files=["LICENSE"]
)
