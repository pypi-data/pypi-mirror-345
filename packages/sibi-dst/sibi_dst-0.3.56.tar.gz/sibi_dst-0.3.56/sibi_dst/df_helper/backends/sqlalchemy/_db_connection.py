from typing import Any, Optional, ClassVar
import threading

from pydantic import BaseModel, model_validator
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text
from sibi_dst.utils import Logger

from ._sql_model_builder import SqlAlchemyModelBuilder

class SqlAlchemyConnectionConfig(BaseModel):
    """
    Configuration class for managing an SQLAlchemy database connection.

    This class provides configurations to establish a connection to a database,
    validate the connection, and dynamically build a SQLAlchemy model for a specific
    table if required. It initializes the database engine using the provided connection URL
    and ensures that the connection and table information are properly validated.

    :ivar connection_url: The URL used to connect to the database.
    :type connection_url: str
    :ivar table: The name of the database table for which a model will be constructed.
    :type table: Optional[str]
    :ivar model: The dynamically built SQLAlchemy model for the specified table.
    :type model: Any
    :ivar engine: The SQLAlchemy engine instance reused for database connections.
    :type engine: Optional[Any]
    """
    connection_url: str
    table: Optional[str] = None
    model: Any = None
    engine: Optional[Any] = None
    logger: Optional[Any] = None
    pool_size: int = 10
    max_overflow: int = 5
    pool_timeout: int = 30
    pool_recycle:int = 300

    # Class-level registry and lock for thread-safe engine reuse
    _engine_registry: ClassVar[dict] = {}
    _registry_lock: ClassVar[threading.Lock] = threading.Lock()

    @model_validator(mode="after")
    def validate_and_initialize(self):
        """
        Validate connection parameters, initialize the engine, and build the dynamic model if necessary.
        """
        if not self.logger:
            self.logger = Logger.default_logger(logger_name=self.__class__.__name__)

        if not self.connection_url:
            raise ValueError("`connection_url` must be provided.")

        # Validate `connection_url`
        if self.engine is not None:
            engine_url = str(self.engine.url)
            if engine_url != self.connection_url:
                raise ValueError(f"Engine URL '{engine_url}' does not match the provided connection URL '{self.connection_url}'.")
        else:
            # Generate a unique key for the engine registry based on the connection URL
            engine_key = (
                self.connection_url,
                self.pool_size,
                self.max_overflow,
                self.pool_timeout,
                self.pool_recycle
            )
            with self.__class__._registry_lock:
                if engine_key in self.__class__._engine_registry:
                    # Reuse the existing engine
                    self.logger.info(f"Reusing existing engine for connection URL: {self.connection_url}")
                    self.engine = self.__class__._engine_registry[engine_key]
                else:
                    # Initialize the engine
                    self.logger.info(f"Creating new engine for connection URL: {self.connection_url}")
                    self.engine = create_engine(self.connection_url,
                                    pool_size=self.pool_size,
                                    max_overflow=self.max_overflow,
                                    pool_timeout=self.pool_timeout,
                                    pool_recycle=self.pool_recycle)
                    self.__class__._engine_registry[engine_key] = self.engine

        # Validate the connection
        self.validate_connection()
        if not self.table:
            raise ValueError("`table_name` must be provided to build the model.")
        try:
            self.model = SqlAlchemyModelBuilder(self.engine, self.table).build_model()
        except Exception as e:
            raise ValueError(f"Failed to build model for table '{self.table}': {e}")

        return self

    def validate_connection(self):
        """
        Test the database connection by executing a simple query.
        """
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except OperationalError as e:
            raise ValueError(f"Failed to connect to the database: {e}")

    @classmethod
    def clear_engine_registry(cls):
        """Clear the global engine registry (useful for testing)."""
        with cls._registry_lock:
            cls._engine_registry.clear()