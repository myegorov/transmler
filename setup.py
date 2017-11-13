from setuptools import setup

setup(name='transmler',
      version='0.1',
      description='syntactic sugar for MLBasis files',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Build Tools',
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
