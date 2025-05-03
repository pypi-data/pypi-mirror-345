from io import open
from setuptools import setup

"""
:authors: DPomortsev
:copyright: (c) 2025 DPomortsev
"""

version = "1.0.7"

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='urban_transit_network_analysis',
    version=version,

    author='DPomortsev',
    author_email='danul78969@gmail.com',

    url='https://github.com/DanilPomortsev/Urban-Transit-Network-Analysis',

    description=(
        u'Python module for urban network analysis'
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=[
        "urban_transit_network_analysis",
        "urban_transit_network_analysis.context",
        "urban_transit_network_analysis.data.calculator",
        "urban_transit_network_analysis.data.preparer",
        "urban_transit_network_analysis.database",
        "urban_transit_network_analysis.enums",
        "urban_transit_network_analysis.graphics",
        "urban_transit_network_analysis.parser",
        "urban_transit_network_analysis.utils"
    ],
    install_requires=['osmnx',
                      'requests',
                      'beautifulsoup4',
                      'neo4j',
                      'pandas',
                      'plotly',
                      'deep-translator',
                      'quads',
                      'numpy',
                      'folium'
                      ]
)
