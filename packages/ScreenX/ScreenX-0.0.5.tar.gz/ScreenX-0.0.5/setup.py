from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    # name="ScrapeX",
    name="ScreenX",
    version="0.0.5",
    description='''The Ultimate AI-Powered Web Automation & Scraping Bot''',
    # package_dir={"": "ScreenX"},
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/ArjanCodes/2023-package",
    author="David C",
    author_email="structureddatadrive@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=["selenium >= 4.24.0","pandas>=2.2.2"],
    extras_require={
        "dev": ["pytest>=7.0", "twine>=4.0.2"],
    },
    python_requires=">=3.6",
)