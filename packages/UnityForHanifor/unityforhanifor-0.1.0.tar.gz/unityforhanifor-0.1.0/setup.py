from setuptools import setup, find_packages

setup(
    name="UnityForHanifor",                # pip’te görünmesini istediğin isim
    version="0.1.0",             # sürüm numarası
    author="Hanifi Ormancı",
    author_email="hanifiormanci@hotmail.com",
    description="UnityForHanifor is a library for Hanifi Ormancı's project.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/hanifor/DeneyapProje",  # varsa repo linki abi
    packages=find_packages(),     # mylib klasöründeki tüm paketleri alır
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
