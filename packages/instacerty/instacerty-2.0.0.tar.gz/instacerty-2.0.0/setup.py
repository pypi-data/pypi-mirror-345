from setuptools import setup, find_packages
setup(
    name="instacerty",
    version="2.0.0",
    description="A python package for generate your certificates/ID cards instantly!",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Madhanraj",
    author_email="madhanreigns312@gmail.com",
    url="https://github.com/iammadhanraj/instacerty",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        'chardet==5.2.0',
        'colorama==0.4.6',
        'pillow==10.4.0',
        'qrcode==8.0',
        'reportlab==4.2.5',
        'python-barcode==0.15.1'
    ],
    include_package_data=True,
    package_data={
        'instacerty': [
            'static/*',
            'id_card_generator/static/fonts/*',
            'id_card_generator/static/templates/*',
            ],
    },
)
