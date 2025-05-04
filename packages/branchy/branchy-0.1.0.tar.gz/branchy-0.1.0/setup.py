from setuptools import setup, find_packages

setup(
    name="branchy",
    version="0.1.0",
    description="A beautiful CLI tool to explore Git branches with style.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Axmadjon Qaxxorov",
    url="https://taplink.cc/itsqaxxorov",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "branchy=branchy.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Software Development :: Version Control :: Git",
        "Intended Audience :: Developers",
    ],
    include_package_data=True,
)
