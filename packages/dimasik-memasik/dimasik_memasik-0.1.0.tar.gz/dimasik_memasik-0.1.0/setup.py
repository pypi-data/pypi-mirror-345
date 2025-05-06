from setuptools import setup, find_packages

setup(
    name="dimasik_memasik",  # Название пакета
    version="0.1.0",    # Версия пакета
    author="Oleg Olegov", # Ваше имя
    author_email="pyukofe2013@gmail.com",  # Ваш email
    description="A short description of your package",  # Краткое описание
    long_description=open("README.md").read(),  # Полное описание из README
    long_description_content_type="text/markdown",  # Тип описания (обычно Markdown)
    packages=find_packages(),  # Автоматическое нахождение всех пакетов
    classifiers=[  # Классификаторы для PyPI
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Минимальная версия Python
)