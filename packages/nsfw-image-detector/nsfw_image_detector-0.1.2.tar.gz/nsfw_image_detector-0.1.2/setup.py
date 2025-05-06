from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nsfw_image_detector",
    version="0.1.2",
    description="A powerful NSFW content detection library using EVA-based vision transformer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Freepik",
    author_email="info@freepik.com",
    url="https://github.com/freepik-company/nsfw_image_detector",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0.0",
        "transformers>=4.30.0",
        "Pillow>=9.0.0",
        "timm>=0.6.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    keywords="nsfw, image-detection, content-filtering, vision-transformer, ai, machine-learning",
) 