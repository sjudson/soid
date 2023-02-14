from setuptools import setup, find_packages

setup(
   name='soid',
   version='0.1',
   description='SMT-based Oracles for Investigating Decisions',
   author='Samuel Judson',
   author_email='samuel.judson@yale.edu',
   packages=find_packages("soid*", exclude=["examples"]),  #same as name
   install_requires=['z3-solver', 'Cython', 'colorama', 'lit', 'pytest', 'scikit-build', 'tabulate', 'toml', 'typing-extensions', 'wllvm', 'zipp'], #external packages as dependencies
)
