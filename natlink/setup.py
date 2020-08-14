from setuptools import setup, find_packages

setup(
    name="natlink",
    version="4.2",
    url="https://github.com/kb100/natlink",
    description="Python scripting environment for Dragon NaturallySpeaking",
    zip_safe=False,  # To unzip documentation files.
    include_package_data=True,
    package_data={'natlink': ['py.typed', '_natlink_core.pyd', '_natlink_core.pyi']},
    install_requires=[
        "setuptools >= 40.0.0",
    ],

    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Win32 (MS Windows)",
        "Intended Audience :: Developers",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
)
