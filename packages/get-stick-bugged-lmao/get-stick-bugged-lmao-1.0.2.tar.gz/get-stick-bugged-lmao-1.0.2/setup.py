import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='get-stick-bugged-lmao',
    version='1.0.2',
    author='n0spaces',
    description="'Get stick bugged' video generator",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/meowscatter/get-stick-bugged-lol',
    packages=setuptools.find_packages(),
    package_data={'gsblmao': ['media/*.*']},
    entry_points={'console_scripts': ['gsblmao=gsblmao.__main__:main']},
    install_requires=['pylsd-nova>=1.2.0', 'numpy', 'Pillow', 'moviepy'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
