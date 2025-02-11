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
        'aiohttp>=3.11.12',
        'anthropic>=0.42.0',
        'click>=8.1.8',
        'instructor>=1.7.2',
        'jinja2>=3.1.5',
        'openai>=1.61.1',
        'pydantic>=2.10.6',
        'requests>=2.32.3',
        'typer>=0.15.1',
    ],
    extras_require={
        'dev': [
            'pytest>=8.3.4',
            'flake8>=7.1.1',
        ],
    },
    entry_points={
        'console_scripts': [
            'minddb=minddb.cli:main',
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
    include_package_data=True,
)
