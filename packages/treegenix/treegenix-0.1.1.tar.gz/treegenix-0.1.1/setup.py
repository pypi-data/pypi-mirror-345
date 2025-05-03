from setuptools import setup, find_packages

setup(
    name="treegenix",
    version="0.1.1",
    author="Sujal Bhagat",
    author_email="sujaldbhagat2004@gmail.com",
    description="A Python CLI tool to generate directory tree structures",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sujal-1245/treegrenix.git",
    project_urls={
        "Bug Tracker": "https://github.com/sujal-1245/treegrenix/issues",
        "Documentation": "https://github.com/sujal-1245/treegrenix/wiki",
    },
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "treegenix=treegen.__main__:main",  # ✅ THIS is what users will type in the terminal
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
    ],
    python_requires='>=3.6',
)
