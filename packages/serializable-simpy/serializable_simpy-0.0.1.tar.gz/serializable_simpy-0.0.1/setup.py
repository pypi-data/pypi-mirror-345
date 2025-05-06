from setuptools import setup, find_packages

setup(
    name='serializable-simpy',
    version='0.0.1',
    description='A simple, yield-less Discrete-Event Simulation library inspired by the SimPy API',
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    author='Pierrick Pochelu',
    author_email='pierrick.pochelu@gmail.com',
    url='https://gitlab.com/uniluxembourg/hpc/research/cadom/serializable-simpy/-/issues',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    include_package_data=True,
)
