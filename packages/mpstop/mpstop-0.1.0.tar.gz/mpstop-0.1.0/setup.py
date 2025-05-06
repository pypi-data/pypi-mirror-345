from setuptools import setup, find_packages

setup(
    name='mpstop',
    version='0.1.0',
    description='Minimal Apple Silicon (MPS) system monitor, nvitop-like for Mac',
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