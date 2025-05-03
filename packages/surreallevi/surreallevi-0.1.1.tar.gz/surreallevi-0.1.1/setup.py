from setuptools import setup, find_packages

setup(
    name='surreallevi',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[],
    author='Erhan Adanur',
    author_email='jjuglans@gmail.com',
    description='A library for Levi-Civita, p-adic, and Surreal number calculations.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)