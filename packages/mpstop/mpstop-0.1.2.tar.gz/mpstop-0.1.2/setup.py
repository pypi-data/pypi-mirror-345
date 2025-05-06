from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README_PYPI.md").read_text(encoding="utf-8")

setup(
    name='mpstop',
    version='0.1.2',
    description='Minimal Apple Silicon (MPS) system monitor, nvitop-like for Mac',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Gokul',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'psutil',
        'torch',
    ],
    entry_points={
        'console_scripts': [
            'mpstop = mpstop.monitor:monitor_gpu',
        ],
    },
    python_requires='>=3.8',
) 