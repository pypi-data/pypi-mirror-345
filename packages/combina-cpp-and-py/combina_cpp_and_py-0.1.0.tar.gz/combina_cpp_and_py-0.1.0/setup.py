from setuptools import setup

with open('README.md') as f:
    long_readme = f.read()
setup(
    name='combina_cpp_and_py',
    version='0.1.0',
    description='Combina C++ and Python code',
    long_description=long_readme,
    long_description_content_type="text/markdown",
    author='Locked-chess-official',
    author_email='13140752715@163.com',
    url='https://github.com/Locked-chess-official/cpppy',
    packages=["combina_cpp_and_py"],
    package_data={
        r'combina_cpp_and_py': ['include/combine.h'],
    },
    include_package_data=True
    
)
