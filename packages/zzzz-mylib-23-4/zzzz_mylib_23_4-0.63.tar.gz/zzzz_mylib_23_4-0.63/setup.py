from setuptools import setup, find_packages

with open("README.md", mode="r") as file:
    description = file.read()

MYLIB_NAME = "zzzz_mylib_23_4"
__version__ = "0.63"  # Chỉnh phiên bản ở đây sau mỗi lần sửa code

REQUIRED_LIBS = [
    # "tensorflow==2.18.0",  # Phiên bản ổn định của TensorFlow
    # "pandas==2.2.2",  # Phiên bản ổn định của Pandas
    # "numpy==1.23.0",  # Phiên bản ổn định của NumPy
    # "matplotlib==3.10.0",  # Phiên bản ổn định của Matplotlib
    # "scikit-learn==1.2.2",  # Phiên bản ổn định của scikit-learn
    # "python-box==6.0.2",  # Phiên bản ổn định của Python-Box
    # "pyYAML==6.0.2",  # Phiên bản ổn định của pyYAML
    # "types-PyYAML==6.0.12.20250402",  # Phiên bản ổn định của types-PyYAML
    # "seaborn==0.13.2",  # Phiên bản mới nhất của Seaborn
    # "xgboost==2.1.4",  # Phiên bản ổn định của XGBoost
    # "lightgbm==4.5.0",  # Phiên bản ổn định của LightGBM
]

setup(
    name=MYLIB_NAME,
    version=__version__,
    packages=find_packages(),
    install_requires=REQUIRED_LIBS,
    long_description=description,
    long_description_content_type="text/markdown",
)
