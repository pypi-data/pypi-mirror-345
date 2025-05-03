import setuptools

PACKAGE_NAME = "user-external-local"
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,  # https://pypi.org/project/user-external-local
    version="0.0.105",
    author="Circles",
    author_email="info@circles.life",
    url=f"https://github.com/circles-zone/{PACKAGE_NAME}-python-package",
    packages=[package_dir],
    package_dir={package_dir: f"{package_dir}/src"},
    package_data={package_dir: ["*.py"]},
    long_description="user-external-local",
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "logger-local>=0.0.61",
        "database-mysql-local>=0.0.83",
        "python-sdk-remote>=0.0.64",
        "user-context-remote>=0.0.54",
        "database-infrastructure-local>=0.0.23",
    ],
)
