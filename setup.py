from setuptools import setup, find_packages
import os

version = '0.1'

long_description = (
    open('README.txt').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='tdf.extensionsuploadcenter',
      version=version,
      description="The LibreOffice Extension upload center",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Plone AddOn LibreOffice Extension Document Foundation TDF',
      author='Andreas Mantke',
      author_email='maand@gmx.de',
      url='http://github.com/andreasma',
      license='gpl',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['tdf', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',

          # -*- Extra requirements: -*-
          'Products.CMFPlone',
          'plone.app.dexterity [grok, relations]',
          'plone.app.referenceablebehavior',
          'plone.app.relationfield',
          'plone.namedfile [blobs]',

          'plone.app.registry',
          'collective.dexteritytextindexer',
          'cioppino.twothumbs',
      ],
      extras_require={'test': ['plone.app.testing[robot]>=4.2.2']},
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
#      setup_requires=["PasteScript"],
#      paster_plugins=["templer.localcommands"],
      )
