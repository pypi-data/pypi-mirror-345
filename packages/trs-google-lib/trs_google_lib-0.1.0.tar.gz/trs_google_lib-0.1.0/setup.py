from setuptools import setup, find_packages

setup(
    name="trs_google_lib",
    version="0.1.0",
    py_modules=["google_trans_simple"],
    packages=find_packages(),
    install_requires=[
        "httpx",
    ],
    author="Ivan Khomich",
    description="Асинхронная библиотека для перевода через Google с поддержкой прокси",
)
