from distutils.core import setup
setup(
  name = 'fitutils',
  packages = ['fitutils'],
  version = '0.3.4',
  license='bsd-3-clause',
  description = 'Utility function and classes for fitting',
  author = 'Marc-Antoine Verdier',
  author_email = 'marc-antoine.verdier@u-paris.fr',
  url = 'https://https://github.com/M-A-Verdier/Fitutils',
  download_url = 'https://github.com/M-A-Verdier/Fitutils/archive/v_0.3.4.tar.gz',
  keywords = ['LeastSquare', 'ErrorBars', 'Fitting'],
  install_requires=[
          'numpy',
          'scipy',
          'matplotlib'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
  ],
)
