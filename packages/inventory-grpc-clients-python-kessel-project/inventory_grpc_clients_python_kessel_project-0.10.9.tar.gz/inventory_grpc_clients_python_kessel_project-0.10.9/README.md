# inventory-grpc-client-python-kessel

This package is generated grpc python client from inventory-api proto files.

## Installation

```shell
$ python -m pip install inventory-grpc-clients-python-kessel-project
```

## Publishing to [PyPI](https://pypi.org/project/inventory-grpc-clients-python-kessel-project/)

### 1. Clone this repo
Run following commands in the root directory.

### 2. Generate a new Python gRPC client

```
 ./generate_python_grpc_client.sh
```
### 3. Push the new version of the package to PyPI

```
 ./publish_to_pypi.sh <new_version>
```
example:
```
 ./publish_to_pypi.sh 0.8.10
```

NOTE: When `./publish_to_pypi.sh` is executed without an argument, the current version is displayed.

### 4. Create PR with new version of python grpc client
The version is included in the commit.
