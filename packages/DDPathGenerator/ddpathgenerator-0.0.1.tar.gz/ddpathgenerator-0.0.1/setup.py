from setuptools import setup, find_namespace_packages

setup(
    name='DDPathGenerator',
    version='0.0.1',
    package_dir={'': 'src'},
    packages=find_namespace_packages(where='src', include='DDPathGenerator.*'),
    python_requires='>=3.8, <4',
    install_requires=[],
)
