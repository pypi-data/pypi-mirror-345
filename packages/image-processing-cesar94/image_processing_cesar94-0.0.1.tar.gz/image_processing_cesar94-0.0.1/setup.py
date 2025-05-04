from setuptools import setup, find_packages
 
with open("README.md", "r") as f:
   page_description = f.read()
 
with open("requirements.txt") as f:
   requirements = f.read().splitlines()
 
setup(
   name="image-processing-cesar94",
   version="0.0.1",
   author="César",
   description="Image Processing Package using Skimage",
   long_description=page_description,
   long_description_content_type="text/markdown",
   url="https://github.com/cesar-a-castro/image-processing-package/",
   packages=find_packages(),
   install_requires=requirements,
   python_requires='>=3.5',
)  
