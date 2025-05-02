from setuptools import setup, find_packages

setup(
    name='rdlab_dataset',
    version='0.4.3',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'rdlab_dataset': ['data/*.pkl', 'font/*.ttf', 'background/*.jpg'],
    },
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='soyvitou',
    author_email='soyvitoupro@gmail.com',
    url='https://github.com/SoyVitouPro/rdlab_dataset',
    install_requires=[
        'matplotlib',
        'Pillow',
        'numpy',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
