from setuptools import setup, find_packages

setup(
    name='cbtope_2',
    version='1.4',
    packages=find_packages(),
    install_requires=[
        'joblib',
        'openpyxl',
        'Bio'
    ],
    author='Nishant Kumar, GPS Raghava',
    author_email='nishantk@iiitd.ac.in, raghava@iiitd.ac.in',
    description='CBTope2: A tool for predicting interactivity of B-cell epitopes',
    url='https://github.com/PandeyAnupma/Cbtope_2',
    python_requires='>=3.7',
    include_package_data=True,
    package_data={
        'cbtope_2.models': ['*.pkl'],
    },
    entry_points={
        'console_scripts': [
            'cbtope2 = cbtope_2.standalone:main'
        ],
    },
)
