import setuptools

PACKAGE_NAME = "google-account-local"

package_dir = PACKAGE_NAME.replace("-", "_")


setuptools.setup(
    name=PACKAGE_NAME,
    version="0.0.11",  # https://pypi.org/project/google-account-local
    author="Circles",
    author_email="info@circlez.ai",
    description=f"PyPI Package for Circles {PACKAGE_NAME} Python",
    long_description=f"PyPI Package for Circles {PACKAGE_NAME} Python",
    long_description_content_type="text/markdown",
    url=f"https://github.com/circles-zone/{PACKAGE_NAME}-python-package",
    packages=[package_dir],
    package_dir={package_dir: f"{package_dir}/src"},
    package_data={package_dir: ["*.py"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "logger-local",
        "database-mysql-local",
        "python-sdk-remote",
        "google-auth-oauthlib>=1.2.0",
        "google-auth-httplib2>=0.2.0",
        "google-api-python-client>=2.128.0",
        "user-external-local>=0.0.42",
    ],
)
