from setuptools import setup, find_packages

setup(
    name='iot-uncertainty',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'python-sat',
        'numpy'
    ],
    author='Your Name',
    author_email='your@email.com',
    description='Hybrid SAT + Probabilistic Modeling for IoT Uncertainty Quantification',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/YOUR_USERNAME/iot-uncertainty',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
