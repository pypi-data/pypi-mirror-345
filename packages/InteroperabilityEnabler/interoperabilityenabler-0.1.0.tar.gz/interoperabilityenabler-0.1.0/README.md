## What is it?

Interoperability Enabler (IE) component is designed to facilitate seamless integration and interaction among various artefacts within the SEDIMARK ecosystem, including data, AI models, and service offerings.


## Key Feature

- Data Formatter - Convert data from various formats into the SEDIMARK internal processing format (pandas DataFrames)
- Data Quality Annotation - Enable adding any kind of quality annotations to data inside pandas DataFrames
- Data Mapper – Convert data from pandas DataFrames into NGSI-LD json
- Data Extractor – Extract relevant data from a pandas DataFrame
- Data Merger – Restore metadata to a pandas DataFrame
- Metadata Restorer – Merge two DataFrames by matching column names

## Installation

The source code can be found on GitHub at https://github.com/Sedimark/InteroperabilityEnabler.

To install the package, you can use pip:

```bash
pip install InteroperabilityEnabler
```

## Project Structure

```text
InteroperabilityEnabler
├── .github
│   └── workflows
│       ├── python-publish.yml
│       └── test.yml
├── InteroperabilityEnabler
│   ├── __init__.py
│   └── utils
│       ├── __init__.py
│       ├── add_metadata.py
│       ├── annotation_dataset.py
│       ├── data_formatter.py
│       ├── data_mapper.py
│       ├── extract_data.py
│       └── merge_data.py
├── MANIFEST.in
├── README.md
├── README_package.md
├── script.py
├── setup.py
└── tests
    ├── __init__.py
    ├── example_json.json
    └── test_basic.py
```

## Acknowledgement

This software has been developed by the [Inria](https://www.inria.fr/fr) under the [SEDIMARK(SEcure Decentralised Intelligent Data MARKetplace)](https://sedimark.eu/) project. 
SEDIMARK is funded by the European Union under the Horizon Europe framework programme [grant no. 101070074]. 
