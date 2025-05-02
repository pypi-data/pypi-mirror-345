import os
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install
import mlagents_envs

VERSION = mlagents_envs.__version__

here = os.path.abspath(os.path.dirname(__file__))


class VerifyVersionCommand(install):
    """
    Custom command to verify that the git tag is the expected one for the release.
    Originally based on https://circleci.com/blog/continuously-deploying-python-packages-to-pypi-with-circleci/
    This differs slightly because our tags and versions are different.
    """

    description = "verify that the git tag matches our version"

    def run(self):
        tag = os.getenv("GITHUB_REF", "NO GITHUB TAG!").replace("refs/tags/", "")

        if tag != VERSION:
            info = "Git tag: {} does not match the version of this app: {}".format(
                tag, VERSION
            )
            sys.exit(info)


# Get the long description from the README file
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="mlgame3d-envs",
    version=VERSION,
    description="Unity Machine Learning Agents Interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PAIA-Playful-AI-Arena/mlgame3d-envs",
    author="PAIA-Tech",
    author_email="service@paia-tech.com",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.11",
    ],
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests", "colabs", "*.ipynb"]
    ),
    zip_safe=False,
    install_requires=[
        "packaging",
        "cloudpickle",
        "grpcio>=1.11.0",
        "Pillow>=4.2.1",
        "protobuf>=3.6,<3.21",
        "pyyaml>=3.1.0",
        "gym>=0.21.0",
        "pettingzoo>=1.23.0",
        "numpy>=1.26,<2.0",
        "filelock>=3.4.0",
    ],
    python_requires=">=3.11",
    cmdclass={"verify": VerifyVersionCommand},  # type: ignore
)
