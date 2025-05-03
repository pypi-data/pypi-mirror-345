from distutils.core import setup
setup(
  name = 'qdiv',
  packages = ['qdiv'],
  version = '3.0.0',
  license='GNU General Public License',
  description = 'Microbial diversity calculations',
  author = 'Oskar Modin',
  author_email = 'omvatten@gmail.com',
  url = 'https://github.com/omvatten/qdiv',
  download_url = 'https://github.com/omvatten/qdiv/archive/refs/tags/v3.0.0.tar.gz',    #Copy address from source code tar.gz on github
  keywords = ['Microbial diversity', 'Amplicon sequencing'],
  install_requires=['pandas', 'numpy', 'matplotlib']
)