from setuptools import setup

setup(
    name='memememe',
    version='1.0.1',
    py_modules=['memememe'],
    install_requires=[
        'requests',
    ],
    author='Seolhwa',
    author_email='znzsndj@gmail.com',
    description='A simple Python module to fetch random GIFs from Tenor.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/memememe',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
