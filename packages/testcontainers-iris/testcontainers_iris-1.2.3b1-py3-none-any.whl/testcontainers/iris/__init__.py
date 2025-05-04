import os
from typing import Optional
from testcontainers.core.generic import DbContainer

# from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import wait_for_logs


class IRISContainer(DbContainer):
    """
    InterSystems IRIS database container.

    Example:

        The example spins up a IRIS database and connects to it using the :code:`intersystems-iris`
        driver.

        .. doctest::

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
    """

    def __init__(
        self,
        image: str = "intersystemsdc/iris-community:latest",
        port: int = 1972,
        username: Optional[str] = None,
        password: Optional[str] = None,
        namespace: Optional[str] = None,
        driver: str = "iris",
        license_key: str = None,
        **kwargs,
    ) -> None:
        # raise_for_deprecated_parameter(kwargs, "user", "username")
        super(IRISContainer, self).__init__(image=image, **kwargs)
        self.image = image
        self.username = username or os.environ.get("IRIS_USERNAME", "test")
        self.password = password or os.environ.get("IRIS_PASSWORD", "test")
        self.namespace = namespace or os.environ.get("IRIS_NAMESPACE", "USER")
        self.port = port
        self.driver = driver
        self.license_key = license_key

        self.with_exposed_ports(self.port)

    def _configure(self) -> None:
        # self.with_env("IRIS_USERNAME", self.username)
        # self.with_env("IRIS_PASSWORD", self.password)
        # self.with_env("IRIS_NAMESPACE", self.namespace)
        if self.license_key:
            self.with_volume_mapping(
                self.license_key, "/usr/irissys/mgr/iris.key", "ro"
            )

    def _connect(self) -> None:
        wait_for_logs(self, predicate="Enabling logons")
        if self.namespace.upper() != "USER":
            cmd = (
                f"iris session iris -U %%SYS '##class(%%SQL.Statement).%%ExecDirect(,\"CREATE DATABASE %s\")'"
                % (self.namespace,)
            )
            res = self.exec(cmd)
            print("res", cmd, res)
        cmd = (
            f'iris session iris -U %%SYS \'##class(Security.Users).Create("%s","%s","%s")\''
            % (
                self.username,
                "%ALL",
                self.password,
            )
        )
        res = self.exec(cmd)
        print("res", cmd, res)

    def get_connection_url(self, host=None) -> str:
        return super()._create_connection_url(
            dialect="iris",
            username=self.username,
            password=self.password,
            dbname=self.namespace,
            host=host,
            port=self.port,
        )
