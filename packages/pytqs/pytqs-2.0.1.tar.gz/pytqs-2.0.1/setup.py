from setuptools import setup

with open("README.md", "r", encoding='utf-8') as f:
    readme = f.read()

setup(name='pytqs',
    version='2.0.1',
    author='Leonardo Pires Batista',
    long_description=readme,
    long_description_content_type="text/markdown",
    url = 'https://github.com/leonardopbatista/pytqs',
    project_urls = {
        'Código fonte': 'https://github.com/leonardopbatista/pytqs',
        'Download': 'https://github.com/leonardopbatista/pytqs'
    },
    author_email='leonardopbatista98@gmail.com',
    keywords='tqs python',
    description=u'Bibliteca para facilitar a integração do Python com o TQS',
    packages=['pytqs','TQS'],
    python_requires='>=3.12',
    install_requires=[
        'pygeometry2d==1.1.3'
        ],
    )

