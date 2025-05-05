from setuptools import setup, find_packages

setup(
    name='mcard',
    version='0.1',
    packages=find_packages(),  # Automatically find packages in the directory
    install_requires=[
        'flask',
        'flask-cors',
        # Add other dependencies here if needed
        'mcard',
    ],
    include_package_data=True,  # Include other files specified in MANIFEST.in
)