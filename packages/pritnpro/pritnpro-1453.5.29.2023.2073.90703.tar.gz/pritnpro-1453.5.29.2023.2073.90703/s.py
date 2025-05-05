from setuptools import setup, find_packages

setup(
    name="pritnpro",  # Paket ismi
    version="1453.5.29.2023.2073.90703",  # Versiyon
    author="h4t1c3libber",  # Kendini yaz
    author_email="h4t1c3libber@turkiye.gov.tr",  # Mailin
    description="Best Print Module.",  # Kısa açıklama
    long_description=open("README.md", encoding="utf-8").read(),  # Uzun açıklama
    long_description_content_type="text/markdown",  # GitHub linkin (varsa)
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # MIT koy kanka, sıkıntı çıkmaz
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Minimum Python versiyonu
)
