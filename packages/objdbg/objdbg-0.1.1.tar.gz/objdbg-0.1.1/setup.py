import setuptools

with open("README.md", "r", encoding='utf8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="objdbg",
    version="0.1.1",
    author="LamentXU",
    author_email="1372449351@qq.com",
    description="Object debugger in python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LamentXU123/objdbg",
    packages=setuptools.find_packages(),
    install_requires=['objprint==0.3.0', 'rich==13.7.1'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)