from setuptools import setup, find_packages

setup(
    name='waterworksai',
    version='2.4.0',
    author='D. Rehn',
    description='The official waterworks.ai python API package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),  # Automatically find the packages in your project,
    include_package_data=True,
    package_data={"": ["assets/*.js"]},
    install_requires=['dash','plotly','pandas','requests','waitress','dash_bootstrap_components','scikit-learn','dash-leaflet','dash-extensions','pysheds', 'geopandas', 'rasterio', 'shapely', 'osmnx'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',  # Specify your required Python version
)

