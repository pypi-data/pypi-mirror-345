from setuptools import setup, find_packages

setup(
    name='image_processing_michelsen',
    version='0.1.0',
    description='Um projeto simples de processamento de imagens usando OpenCV',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Juliana',
    author_email='juju.michelsen@gmail.com',
    url='https://github.com/JulianaMichelsen/IMAGE-PROCESSING-PYTHON.git',  # se tiver GitHub
    packages=find_packages(),
    install_requires=[
        'opencv-python>=4.0.0',
        'numpy'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.13',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
