from setuptools import setup, find_packages

with open("./README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()
setup(
    name='pylinreglib',
    version='0.1.1',
    description='Biblioteca de libre desarrollo especializada en regresiones lineales',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Samuel Ortiz Toro',
    author_email='saortizt@unal.edu.co',
    url='https://github.com/SamuelOrtizT/pylinreglib',
    packages=find_packages(),
    install_requires=[
    'numpy',            # Para la manipulación de arrays y operaciones matemáticas
    'pandas',           # Para trabajar con DataFrames
    'scipy',            # Para funciones estadísticas como f, t y shapiro
    'matplotlib',       # Para gráficos
    'seaborn',          # Para visualización estadística avanzada
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Development Status :: 3 - Alpha',
    ],
    python_requires='>=3.8',
    license='MIT',
    include_package_data=True
)
