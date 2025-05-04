
from setuptools import setup, find_packages

setup(
    name="KARLOM_v1",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "KARLOM_v1": ["images/*.png", "images/*.jpg", "images/*.jpeg"]
    },
    install_requires=[
        "Pillow"
    ],
    entry_points={
        "console_scripts": [
            "karlom=KARLOM_v1.KARLOM_v1:main"
        ]
    },
    author="Tvé jméno",
    description="Grafický logický simulátor a minimalizátor logických funkcí",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
