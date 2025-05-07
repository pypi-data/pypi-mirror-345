from setuptools import setup, find_packages

setup(
    name='deapp',       # Replace with your package name
    version='0.1.1',
    author='Your Name',
    author_email='your.email@example.com',
    description='A short description of your package',
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/your_package_name', # Optional
    packages=find_packages(),
    install_requires=[],  # List of dependencies
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
