from setuptools import setup, find_packages

setup(
    name='wordsim',  # Replace with your package name
    version='0.1.0',  # Initial version number
    packages=find_packages(),  # Automatically find all package subdirectories
    install_requires=[
        # List any dependencies your package needs, e.g.,
        # 'requests >= 2.20',
    ],
    author='Khaled Terzaki',  # Your name
    author_email='khaled.m.terzaki@gmail.com',  # Your email address
    description='This is simply a word similarity model that matches the desired word to the most similar word in a reference list of words provided by the user.',
    license='MIT',
    python_requires='>=3.9',
    long_description=open('README.md').read(),  # Optional: Read long description from README
    long_description_content_type='text/markdown',  # If using Markdown for long description
    url='https://github.com/Khaled-Terzaki/wordsim.git',  # Optional: Link to your repository
    classifiers=[
        'Development Status :: 3 - Alpha',  # As you mentioned it is still under testing
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12', #Added for completeness
        'Topic :: Text Processing :: Linguistic',  # Added a relevant classifier
    ],
)