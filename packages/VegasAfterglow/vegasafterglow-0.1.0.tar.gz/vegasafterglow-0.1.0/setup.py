from setuptools import setup, Extension, find_packages
import os
import platform
import pybind11

def find_sources():
    sources = ["pybind/pybind.cpp", "pybind/mcmc.cpp"]
    for root, _, files in os.walk("src"):
        for fn in files:
            if fn.endswith(".cpp"):
                sources.append(os.path.join(root, fn))
    return sources

system = platform.system()
archflags = os.environ.get("ARCHFLAGS", "")

# Base flags
extra_compile_args = []
extra_link_args = []

# Platform-specific settings
if system == "Linux":
    extra_compile_args = ["-std=c++20", "-O3", "-flto", "-w", "-DNDEBUG", "-fPIC", "-ffast-math", "-pipe"]
    extra_link_args = []

elif system == "Darwin":
    extra_compile_args = ["-std=c++20", "-O3", "-flto", "-w", "-DNDEBUG", "-fPIC", "-ffast-math", "-pipe"]
    extra_link_args = ["-undefined", "dynamic_lookup"]
    # Don't use -march=native for universal builds
    #if "-arch arm64" not in archflags or "-arch x86_64" not in archflags:
    #    extra_compile_args.append("-march=native")

elif system == "Windows":
    extra_compile_args = ["/std:c++20", "/O2", "/DNDEBUG", "/fp:fast", "/MP", "/GL"]
    extra_link_args = ["/LTCG"]

ext_modules = [
    Extension(
        "VegasAfterglow.VegasAfterglowC",
        sources=find_sources(),
        include_dirs=[
            pybind11.get_include(),
            "include",
            "external"
        ],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        language="c++",
    )
]

setup(
    name="VegasAfterglow",
    version="0.1.0",
    description="MCMC tools for astrophysics",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Yihan Wang, Connery Chen, Bing Zhang",

    license="MIT",                         # SPDX expression only
    data_files=[("", ["LICENSE"])],

    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.19",
        "pandas>=1.1",
        "emcee>=3.0",
        "pybind11>=2.6.0",
        "corner>=2.2.1",
        "tqdm>=4.0",
        "scipy>=1.10",
    ],
    extras_require={
        "dev": ["ninja", "pytest", "black"],
    },

    packages=find_packages(where="pymodule"),
    package_dir={"": "pymodule"},

    ext_modules=ext_modules,
    zip_safe=False,
    include_package_data=True,
    )