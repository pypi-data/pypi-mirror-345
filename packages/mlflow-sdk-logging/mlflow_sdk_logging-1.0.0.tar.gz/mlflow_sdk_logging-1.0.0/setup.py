from setuptools import setup, find_packages
setup(
    name='mlflow_sdk_logging',
    version='1.0.0',
    packages=find_packages(),
    description='Log parameters, metrics, and artifacts using MLflow.',
    author='Radhika Menon',
    author_email='Radhika.Menon@cognizant.com',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Choose your license
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)