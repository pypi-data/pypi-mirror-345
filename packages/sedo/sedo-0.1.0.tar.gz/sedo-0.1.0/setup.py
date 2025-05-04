from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("LICENSE", "r", encoding="utf-8") as fh:
    license = fh.read()

setup(
    name="sedo",
    version="0.1.0",
    author="safe049",
    author_email="safe049@163.com",
    description="Social Entropy Diffusion Optimization Algorithm (SEDO)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/safe049/sedo",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence"
    ],
    python_requires='>=3.8',
    install_requires=[
        "numpy",
        "scipy",
        "matplotlib"
    ],
    extras_require={
        "dev": [
            "pytest",
            "sphinx"
        ]
    },
    include_package_data=True,
)