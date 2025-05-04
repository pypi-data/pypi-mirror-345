from setuptools import setup, find_packages

setup(
    name='trc',
    version='0.4',
    packages=find_packages(),
    install_requires=['requests', 'pillow', 'psutil'],
    author='TRC-Team',
    description="trc is a Python package designed to enhance the language's capabilities by providing a collection of practical utility functions." \
    " These functions aim to simplify common programming tasks, making code more concise and readable." \
    " Whether you're cleaning strings, manipulating data structures, or performing routine operations, trc offers tools to streamline your development process.",
    license='MIT',
)