import os

from setuptools import setup, find_packages
#from fastpluggy import __version__

# Function to read the requirements from the requirements.txt file
def parse_requirements(filename):
    """Load requirements from a pip requirements file."""
    with open(filename, 'r') as req_file:
        return [line.strip() for line in req_file if line and not line.startswith("#")]


requirements = []
if os.path.isfile("requirements.txt"):
    requirements = parse_requirements("requirements.txt")
else:
    print("requirements.txt not found")

print(f"requirements: {requirements}")

setup(
    name='FastPluggy',
    version="0.2.7",
    description='A FastAPI-based framework with plugin management and database handling.',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://gitlab.ggcorp.fr/open/fastpluggy/fast_pluggy',
    packages=find_packages(where='src'),  # This finds all packages under src/
    package_dir={'': 'src'},  # Tells setuptools that all packages are under the src directory
    include_package_data=True,  # This includes non-code files (static, templates)
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
