from setuptools import setup, find_packages

setup(
    name="model_monitoring",
    version="2.0.5",
    description="Package for Model Monitoring",
    author="DAT Team",
    url="https://dev.azure.com/credem-data/DAT/_git/model_monitoring",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
    ],
    packages=find_packages(where="src"),
    package_data={
        "model_monitoring": ["config/*.yml"],
    },
    include_package_data=True,
    package_dir={"": "src"},
    # Usato solo con 3.9 e 3.10
    python_requires=">=3.9, <4",
    install_requires=[
        "typed-ast==1.5.4",
        "numpy==1.22.4",
        "pandas==1.5.3",
        "scikit-learn==1.2.1",
        "lightgbm==3.3.2",
        "scipy==1.10.1",
        "PyYAML==6.0",
        "shap==0.41.0",
        "ipython",
        "numba==0.60.0",
    ],
)
