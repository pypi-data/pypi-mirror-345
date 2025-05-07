from setuptools import setup, find_packages

setup(
    name='djstart',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'requests',
        'jinja2',
    ],
    entry_points={
        'console_scripts': [
            'djstart=djstart.main:main',
        ],
    },
    author='Ajay',
    author_email='your.email@example.com',
    description='A simple CLI tool to scaffold Django projects and apps',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/djstart',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
