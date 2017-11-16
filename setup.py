from setuptools import setup
from os import path

root = path.abspath(path.dirname(__file__))
with open(path.join(root, 'README.md')) as readme:
    long_description = readme.read()

setup(name='transmler',
      version='0.3',
      description='syntactic sugar for MLBasis files',
      long_description=long_description,
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Build Tools',
        'Intended Audience :: Developers',
      ],
      keywords='transpiler sml mlton import export',
      url='https://github.com/myegorov/transmler',
      author='Maksim Yegorov',
      author_email='findmaksim@gmail.com',
      license='MIT',
      packages=['transmler'],
      entry_points={ 'console_scripts': ['transmile=transmler.run:main']
      },
      python_requires='>=3.0',
      setup_requires=['setuptools-git']
)
