from setuptools import setup, find_packages

setup(
    name="ht-serve",
    version="0.0.3",
    description="Secure HTTPS live reload server for UI/dashboard development",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="HermiTech Labs",
    author_email="support@hermitech.dev",
    url="https://github.com/HermiTech-LLC/HT-Serve",
    packages=find_packages(exclude=["tests*", "docs*"]),
    include_package_data=True,
    install_requires=[
        "watchdog>=3.0",
        "rich>=13.0",
        "websockets>=11.0",
        "typer[all]>=0.9"
    ],
    entry_points={
        "console_scripts": [
            "ht-serve = ht_serve.cli:app"
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Testing"
    ],
    python_requires='>=3.8',
    zip_safe=False
)
