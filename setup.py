from setuptools import setup, find_packages

description = ("Automates the creation of Anki flashcards from course "
               "transcripts")
setup(
    name="minddb",
    version="0.1.0",
    description=description,
    author="Your Name",  # You can update this
    packages=find_packages(),
    install_requires=[
        # Add your dependencies here, for example:
        # 'requests>=2.25.1',
    ],
    entry_points={
        'console_scripts': [
            'minddb=bin.cli:main',
        ],
    },
    python_requires='>=3.12',  # Specify minimum Python version
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.12',
    ],
)
