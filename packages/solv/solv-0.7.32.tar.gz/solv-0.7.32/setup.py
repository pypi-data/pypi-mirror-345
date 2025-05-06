from skbuild import setup

# This is fragile, but "good enough for now"
with open('VERSION.cmake', 'r+') as version_file:
    lines = version_file.read().splitlines()[-4:-1]
    # parse out digit characters from the line, convert to int
    numbers = [int("".join(filter(str.isdigit, line))) for line in lines]
    # build version string
    version = '{major}.{minor}.{patch}'.format(
        major=numbers[0],
        minor=numbers[1],
        patch=numbers[2]
    )

with open('README', 'r+') as readme:
    README = readme.read()

setup(
    name='solv',
    description='A free package dependency solver using a satisfiability algorithm.',
    long_description_content_type="text/markdown",
    long_description=README,
    version=version,
    license='BSD',
    author='',
    author_email='',
    url='',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: C',
        'Topic :: System :: Software Distribution',
        'Topic :: System :: Systems Administration',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    packages=['solv'],
    package_dir={
        'solv': 'bindings/python3'
    },
    cmake_args=[
        '-DCMAKE_BUILD_TYPE:STRING=RelWithDebInfo',
        '-DENABLE_PYTHON3:BOOL=ON',
        '-DENABLE_COMPLEX_DEPS:BOOL=ON',
        '-DENABLE_RPMMD:BOOL=ON',
        '-DENABLE_STATIC:BOOL=ON',
        '-DENABLE_STATIC_BINDINGS:BOOL=ON',
        '-DWITH_LIBXML2:BOOL=ON',
    ],
    cmake_languages=['C'],
)
