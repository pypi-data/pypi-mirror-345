from setuptools import setup, find_packages

setup(
    name="elrahdjango",
    version="0.0.1",
    packages=find_packages(),
    description="Package personnalisé pour optimiser le développement avec django",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Harlequelrah",
    author_email="maximeatsoudegbovi@example.com",
    url="https://github.com/Harlequelrah/Library-ElrahDjango",
    python_requires=">=3.10",
    install_requires=[
        "django>=5.2",
    ],
)
