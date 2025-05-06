from setuptools import setup, find_packages

setup(
    name="ashiart",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pillow>=10.0.0",
        "numpy>=1.20.0",
    ],
    entry_points={
        'console_scripts': [
            'ashiart=ashiart.cli:main',
        ],
    },
    author="Faycal Amrouche",
    author_email="example@example.com",
    description="A package for generating ASCII art from images",
    keywords="ascii, art, image, converter",
    python_requires=">=3.6",
) 