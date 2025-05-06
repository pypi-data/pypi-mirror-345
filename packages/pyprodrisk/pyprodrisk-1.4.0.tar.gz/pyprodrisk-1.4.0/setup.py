from distutils.core import setup
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')


setup(name='pyprodrisk',
      version='1.4.0',
      author='SINTEF Energy Research',
      description='Python interface to Prodrisk',
      long_description=long_description,
      long_description_content_type='text/markdown',
      packages=['pyprodrisk',
                'pyprodrisk.helpers',
                'pyprodrisk.prodrisk_core'],
      package_dir={'pyprodrisk': 'pyprodrisk',
                   'pyprodrisk.helpers': 'pyprodrisk/helpers',
                   'pyprodrisk.prodrisk_core': 'pyprodrisk/prodrisk_core'},
      url='http://www.sintef.no/programvare/Prodrisk',
      project_urls={
          'Documentation': 'https://docs.prodrisk.sintef.energy/examples/interacting_prodrisk/pyprodrisk_basic/pyprodrisk_basic.html',
          'Source': 'https://gitlab.sintef.no/energy/prodrisk/pyprodrisk',
          'Tracker': 'https://prodrisk.sintef.energy/tickets',
      },
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: MIT License',
          'Intended Audience :: Developers',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Education',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
#          'Programming Language :: Python :: 3.13',
          'Operating System :: POSIX :: Linux',
          'Operating System :: Microsoft :: Windows',
      ],
      author_email='support.energy@sintef.no',
      license='MIT',
      python_requires='>=3.9',
      install_requires=['pandas', 'numpy', 'graphviz', 'pybind11'],
      extras_require={
        'full': [
            # optional dependencies for dumping/reading data
            'pyyaml',
            'tables',
            # optional dependencies for topology plot
            'scipy',
            'matplotlib',
        ]
    },
    )
