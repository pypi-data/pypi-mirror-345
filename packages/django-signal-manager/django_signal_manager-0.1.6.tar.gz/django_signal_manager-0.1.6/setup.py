from setuptools import find_packages, setup

setup(
    name="django_signal_manager",
    version="0.1.6",
    author="Konrad Beck",
    author_email="konradbeck101@gmail.com",
    description="A package for managing Django model signals.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/konradbeck/django-signal-manager.git",
    packages=find_packages(where='.', include=["django_signal_manager", "django_signal_manager.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
    ],
    python_requires=">=3.6",
    install_requires=[
        "django>=3.0",
    ],
    extras_require={
        "dev": ["pytest", "pytest-django"],
    }
)
