# DDSAPI-Client
Python Client to access and download data from [CMCC Data Delivery System (DDS)](https://dds.cmcc.it)

## Requirements
Python 3.7, Python 3.8

### Installation  
Conda Installation
```bash
$ conda install -c fondazione-cmcc ddsapi 
```

Pip installation
```bash
$ pip install ddsapi
```

### Configuration
To use the tool a file `$HOME/.ddsapirc` must be created as following

```bash
url: https://ddshub.cmcc.it/api/v2
key: <api-key>
```