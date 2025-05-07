# setup.py (root of your project)
import os
from glob import glob
from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import numpy

#print(find_packages())  

# 
# 1. Locate all .pyx files in pybmesh/cython/src
# 
cython_src_dir = os.path.join("pybmesh", "cython", "src")
pyx_files = glob(os.path.join(cython_src_dir, "*.pyx"))

# 
# 2. Create Extension objects for each .pyx
#    name them pybmesh.cython.<module>, so the .so
#    lands in pybmesh/cython/
# 
extensions = []
for path in pyx_files:
    mod_name = os.path.splitext(os.path.basename(path))[0]
    full_module = f"pybmesh.cython.{mod_name}"
    # face_extractor needs C++ linkage; others are plain C
    language = "c++" if mod_name.lower() == "face_extractor" else "c"
    extensions.append(
        Extension(
            full_module,
            [path],
            include_dirs=[numpy.get_include()],
            language=language,
        )
    )

# 
# 3. Read long description from your README
# 
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# 
# 4. Call setup()
# 
setup(
    name="pybmesh",
    version="1.0.1",
    author="Alexis Sauvageon",
    author_email="alexis.sauvageon@arep.fr",
    description="A meshing tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/alexis.sauvageon/pybmesh.git",

    # packages: find everything under pybmesh/, but skip examples & tests
    packages=find_packages(exclude=["examples*", "tests*"]),

    # runtime dependencies
    install_requires=[
        "gmsh==4.13.1",
        "matplotlib==3.10.1",
        "numpy==2.2.3",
        "pandas==2.2.2",
        "pyside6==6.9.0",
        "scikit_learn==1.6.1",
        "scikit-spatial==8.1.0",
        "scipy==1.15.2",
        "vtk==9.3.1",
    ],

    # compile Cython extensions
    #ext_modules=cythonize(extensions, compiler_directives={"language_level": "3"}),
    ext_modules = cythonize(
        extensions,
        force=True,
        compiler_directives={"language_level": "3"},
    ),
    # ensure compiled .so files and other resources get included
    include_package_data=True,
    package_data={
        "pybmesh": [
					"ressources/images/*.png",
					"ressources/foamTimeWriter/*.pkl",
					],
    },

    zip_safe=False,

    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
)
