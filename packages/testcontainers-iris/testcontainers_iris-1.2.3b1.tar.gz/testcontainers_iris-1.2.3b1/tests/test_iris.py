import os
import sqlalchemy
from testcontainers.iris import IRISContainer

creds = {
    "username": "test",
    "password": "test",
    "namespace": "TEST",
}


def check_connection(iris):
    engine = sqlalchemy.create_engine(iris.get_connection_url())
    with engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("select $username, $namespace"))
        assert result.fetchone() == (creds["username"], creds["namespace"])


def test_community():
    iris_container = IRISContainer("containers.intersystems.com/intersystems/iris-community:latest-em", **creds)
    with iris_container as iris:
        check_connection(iris)


def test_dccommunity():
    iris_container = IRISContainer("intersystemsdc/iris-community:latest", **creds)
    with iris_container as iris:
        check_connection(iris)


def test_enterprise():
    license_key = os.path.abspath(os.path.expanduser("~/iris.key"))
    iris_container = IRISContainer("containers.intersystems.com/intersystems/iris:latest-cd", license_key=license_key,
                                   **creds)
    with iris_container as iris:
        check_connection(iris)
