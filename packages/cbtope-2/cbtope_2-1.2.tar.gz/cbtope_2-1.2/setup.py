from setuptools import setup, find_packages

setup(
    name='cbtope_2',
    version='1.2',
    packages=find_packages(),
    install_requires=[
        'joblib',
        'scikit-learn',
        'numpy',
        'openpyxl',
        'Bio'
    ],
    author='Nishant Kumar',
    author_email='nishantk@iiitd.ac.in',
    description='CBTope2: A tool for predicting interactivity of B-cell epitopes',
    url='https://github.com/Megha2k/cbtope_2',
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
