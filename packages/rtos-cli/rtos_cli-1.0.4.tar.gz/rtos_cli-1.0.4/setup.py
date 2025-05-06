from setuptools import setup, find_packages

setup(
    name='rtos_cli',
    version='1.0.4',
    packages=find_packages(include=['rtos_cli', 'rtos_cli.*']),
    include_package_data=True,
    install_requires=[],
    entry_points={
        'console_scripts': [
            'rtos_cli = rtos_cli.rtos_cli:main',
        ],
    },
    author='Efrain Reyes Araujo',
    author_email='dev@reyes-araujo.com',
    description='CLI para automatizar proyectos PlatformIO con FreeRTOS',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)