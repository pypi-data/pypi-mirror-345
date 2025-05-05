from setuptools import setup, find_packages

setup(
    name="ideal6",
    version="1.0.0",
    description="Multi-layer AES encryption library",
    author="اسمك",
    author_email="بريدك@example.com",
    url="https://github.com/yourname/ideal6",  # اختياري
    packages=find_packages(),
    install_requires=[
        "pycryptodome"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">=3.6",
)