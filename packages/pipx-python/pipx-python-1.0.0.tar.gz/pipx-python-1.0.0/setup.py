import setuptools
import distutils.core

setuptools.setup(
    name='pipx-python',
    version="1.0.0",
    author='talwrii',
    long_description_content_type='text/markdown',
    author_email='talwrii@gmail.com',
    description='Run the version of python corresponding to an executable installed with pipx',
    license='MIT',
    keywords='pipx,python,virtualenv',
    url='https://github.com/talwrii/pipx-python',
    packages=["pipx_python"],
    long_description=open('README.md').read(),
    entry_points={
        'console_scripts': ['pipx-python=pipx_python.main:main']
    }
)
