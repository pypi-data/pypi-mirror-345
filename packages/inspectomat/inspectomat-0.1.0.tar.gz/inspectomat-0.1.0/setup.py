from setuptools import setup, find_packages

setup(
    name="inspectomat",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'inspectomat=inspectomat.cli:main',
        ],
    },
    install_requires=[
        'setuptools',
    ],
    extras_require={
        'full': [
            'pillow',  # For image processing
            'numpy',   # For array operations
            'tqdm',    # For progress bars
            'psutil',  # For system information
        ],
    },
    author="multigit-com",
    description="System cleanup and file management toolbox",
    keywords="cleanup, file management, deduplication",
    python_requires=">=3.6",
    test_suite="tests",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "Intended Audience :: End Users/Desktop",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
