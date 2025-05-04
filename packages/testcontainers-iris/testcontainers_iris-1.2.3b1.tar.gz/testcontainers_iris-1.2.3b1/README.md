# Testcontainers-python for InterSystems IRIS

[testcontainers-python](https://testcontainers-python.readthedocs.io/en/latest/README.html) facilitates the use of Docker containers for functional and integration testing.

## Other implementations

* [testcontainers-iris-java](https://github.com/caretdev/testcontainers-iris-java)

## Basic usage

```
>>> from testcontainers.iris import IRISContainer
>>> import sqlalchemy

>>> iris_container = IRISContainer("intersystemsdc/iris-community:latest")
>>> with iris_container as iris:
...     engine = sqlalchemy.create_engine(iris.get_connection_url())
...     with engine.begin() as connection:
...         result = connection.execute(sqlalchemy.text("select $zversion"))
...         version, = result.fetchone()
>>> version
'IRIS for UNIX (Ubuntu Server LTS for ARM64 Containers) 2023.2 (Build 227U) Mon Jul 31 2023 17:43:25 EDT'
```

The snippet above will spin up a InterSystems IRIS database in a container. The get_connection_url() convenience method returns a sqlalchemy compatible url we use to connect to the database and retrieve the database version.

It is possible to run Enterprise edition as well, with passing a valid iris.key.

```python
iris_container = IRISContainer(
    "containers.intersystems.com/intersystems/iris:2023.3", 
    license_key="/full/path/to/iris.key",
    username="testuser",
    password="testpass",
    namespace="TEST",
)

```

`username`, `password`, `namespace` will be created during start of the container with required values, user will get %All role

[Demo](iris.ipynb) with Jupiter Notebook 

More extensive documentation can be found at [Read The Docs](https://testcontainers-python.readthedocs.io/).