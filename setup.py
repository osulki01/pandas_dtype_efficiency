import pathlib
import setuptools

package_name = 'pandas_dtype_efficiency'
version = '0.0.1'

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setuptools.setup(
    author="Kieran O'Sullivan",
    author_email='osullivank3@hotmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
    description='Evaluate pandas DataFrames to see whether their memory usage can be reduced without losing '
                'information',
    install_requires=['pandas'],
    keywords=['data', 'science', 'pandas', 'memory', 'efficiency'],
    license='MIT',
    long_description=README,
    long_description_content_type="text/markdown",
    name=package_name,
    py_modules=['pandas_dtype_efficiency'],
    python_requires='>=3.7',
    url='https://github.com/osulki01/pandas_dtype_efficiency',
    version=version,
)
