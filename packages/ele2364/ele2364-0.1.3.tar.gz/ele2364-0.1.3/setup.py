from setuptools import setup, find_packages

try:
    with open('README.md', 'r') as fh:
        long_description = fh.read()
except:
    long_description = ''

setup(name='ele2364',
      version='0.1.3',
      description='ELE2364 (reinforcement learning) support package',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://github.com/wcaarls/ele2364',
      author='Wouter Caarls',
      author_email='wouter@puc-rio.br',
      license='MIT',
      classifiers=['Development Status :: 4 - Beta',
      'Environment :: Console',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python :: 3',
      'Topic :: Education',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      ],
      keywords='reinforcement learning',
      packages=find_packages(),
      package_data={'ele2364.flappy_bird_gym.assets.sprites': ['*.png']},
      install_requires=['numpy', 'gymnasium', 'pygame', 'torch >= 2.1.0'],
      entry_points = {}
     )
