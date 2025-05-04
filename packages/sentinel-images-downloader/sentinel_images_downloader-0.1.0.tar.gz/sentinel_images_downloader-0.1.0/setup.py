from setuptools import setup, find_packages

setup(
    name="sentinel_images_downloader",
    version="0.1.0",
    author="SaN4OuSl",
    author_email="oleksandr.laptiev.work@gmail.com",
    description="Download Sentinel-1 and Sentinel-2 images from Copernicus Data Space",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/SaN4OuSl/sentinel_images_downloader",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    install_requires=["requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: GIS"
    ],
    python_requires=">=3.7",
)
