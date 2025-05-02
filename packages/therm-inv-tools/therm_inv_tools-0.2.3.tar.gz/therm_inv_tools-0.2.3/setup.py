import setuptools 
  
with open("README.md", "r") as fh: 
    description = fh.read() 
  
setuptools.setup( 
    name="therm_inv_tools", 
    version="0.2.3", 
    author="Anthony R. Osborne", 
    author_email="anthony.osborne019@gmail.com", 
    packages=["tools"], 
    description="A package containing all my tools for thermal inversions", 
    long_description=description, 
    long_description_content_type="text/markdown", 
    url="https://github.com/Anthony904175/therm_inv_tools.git", 
    license='MIT', 
    python_requires='>=3.8', 
    install_requires=[] 
) 
