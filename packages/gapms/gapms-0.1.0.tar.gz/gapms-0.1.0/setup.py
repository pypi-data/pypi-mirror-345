from setuptools import setup, find_packages

setup(
    name='gapms',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'biopython',
        'matplotlib',
        'seaborn',
        'scipy',
        'scikit-learn',
        'xgboost',
        'shap',
        'psauron',
    ],
    entry_points={
        'console_scripts': [
            'gapms=gapms.main:main',
        ],
    },
)
