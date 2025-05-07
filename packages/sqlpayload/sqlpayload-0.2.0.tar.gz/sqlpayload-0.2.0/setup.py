from setuptools import setup, find_packages

setup(
    name='sqlpayload',
    version='0.2.0',
    description='Automated proxy login brute-forcer via Burp Suite',
    author='Your Name',
    author_email='your_email@example.com',
    packages=find_packages(),
    install_requires=[
        'requests',
        'keyboard',
        'urllib3'
    ],
    entry_points={
        'console_scripts': [
            'sqlpayload=sqlpayload.core:main'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: Microsoft :: Windows',
    ],
    python_requires='>=3.6',
)
