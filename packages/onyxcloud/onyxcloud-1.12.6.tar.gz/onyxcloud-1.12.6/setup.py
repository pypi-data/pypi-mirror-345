from setuptools import setup, find_packages

setup(
    name="onyxcloud",
    version="1.12.6",
    description="Python package for the OnyxCloud CTF challenge. Part 1",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    author="CTFByte",
    author_email="dev@ctfbyte.com",
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    package_data={'onyxcloud': ['onyxcloud.chat.py', 'onyxcloud.Utils.py', 'onyxcloud.utils/*' 'onyxcloud.__init__.py', 'model/modelpt', 'model/model']},
    include_package_data=True,
    install_requires=[
        "torch==2.6.0",
        "numpy==2.1.3",
        "pypac==0.16.5",
        "matplotlib==3.9.3",
        "requests==2.32.3",
        "ctfbyte-colorama==0.5.2",
        "requests-kerberos==0.15.0",
        "pywin32==310",
    ],
    # UNCOMMENT to enable console script entry point
    # This will allow you to run the package from the command line using `onyxcloud`
    # entry_points={
    #     "console_scripts": [
    #         "onyxcloud=onyxcloud.chat:chat",
    #     ],
    # },
)

