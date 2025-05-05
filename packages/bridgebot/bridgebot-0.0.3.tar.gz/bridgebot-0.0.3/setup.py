import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bridgebot",
    version="0.0.3",
    author="Papan Yongmalwong",
    author_email="papillonbee@gmail.com",
    description="bridgebot is a python package for building floating bridge bot!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/papillonbee/bridgebot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment",
    ],
    python_requires='>=3.10',
    install_requires=[
        "ray[rllib]==2.45.0",
        "torch==2.2.2",
        "bridgepy==0.0.13",
    ],
    keywords=[
        "reinforcement learning",
        "floating bridge",
        "singaporean bridge",
    ],
)

# pip3 install -e .
# pip3 install setuptools wheel twine
# python3 setup.py sdist bdist_wheel
# twine upload dist/*
