from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()
setup(
    name="elrahdjango",
    version="0.0.2",
    packages=find_packages(),
    description="Package personnalisé pour optimiser le développement avec django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Harlequelrah",
    author_email="maximeatsoudegbovi@example.com",
    url="https://github.com/Harlequelrah/Library-ElrahDjango",
    maintainer="jordanBuilder",
    maintainer_email="tomegahjordan81@gmail.com",
    license="LGPL-3.0-only",
    python_requires=">=3.10",
    install_requires=[
        "django>=5.2",
    ],
)
