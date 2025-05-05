import os
from contextlib import contextmanager
from sqlalchemy import MetaData
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import Generator, Optional, Type
from maleo_foundation.types import BaseTypes
from maleo_foundation.utils.logger import BaseLogger
from .table import BaseTable

class DatabaseManager:
    Base:DeclarativeMeta = declarative_base()  #* Correct way to define a declarative base

    #* Explicitly define the type of metadata
    metadata:MetaData = Base.metadata

    @classmethod
    def initialize(cls, engine:Engine):
        """Creates the database tables if they do not exist."""
        cls.metadata.create_all(engine)

class MetadataManager:
    _Base:DeclarativeMeta = declarative_base()

    @property
    def Base(self) -> DeclarativeMeta:
        return self._Base

    @property
    def metadata(self) -> MetaData:
        return self._Base.metadata

class SessionManager:
    def __init__(self, logger:BaseLogger, engine:Engine):
        self._logger = logger
        self._sessionmaker:sessionmaker[Session] = sessionmaker(bind=engine, expire_on_commit=False)
        self._logger.info("SessionManager initialized successfully.")

    def _session_handler(self) -> Generator[Session, None, None]:
        """Reusable function for managing database sessions."""
        if self._logger is None:
            raise RuntimeError("Logger has not been initialized. Call initialize() first.")
        if self._sessionmaker is None:
            raise RuntimeError("SessionLocal has not been initialized. Call initialize() first.")

        session = self._sessionmaker()
        self._logger.debug("New database session created.")
        try:
            yield session  #* Provide session
            session.commit()  #* Auto-commit on success
        except SQLAlchemyError as e:
            session.rollback()  #* Rollback on error
            self._logger.error(f"[SQLAlchemyError] Database transaction failed: {e}", exc_info=True)
            raise
        except Exception as e:
            session.rollback()  #* Rollback on error
            self._logger.error(f"[Exception] Database transaction failed: {e}", exc_info=True)
            raise
        finally:
            session.close()  #* Ensure session closes
            self._logger.debug("Database session closed.")

    def inject(self) -> Generator[Session, None, None]:
        """Returns a generator that yields a SQLAlchemy session for dependency injection."""
        return self._session_handler()

    @contextmanager
    def get(self) -> Generator[Session, None, None]:
        """Context manager for manual session handling. Supports `with SessionManager.get() as session:`"""
        yield from self._session_handler()

    def dispose(self) -> None:
        """Dispose of the sessionmaker and release any resources."""
        if self._sessionmaker is not None:
            self._sessionmaker.close_all()
            self._sessionmaker = None

        self._logger.info("SessionManager disposed successfully.")
        self._logger = None

class DatabaseManagerV2:
    # _metadata:Optional[MetaData] = None
    # _logger:Optional[BaseLogger] = None
    # _engine:Optional[Engine] = None
    # _session:Optional[SessionManager] = None

    def __init__(
        self,
        metadata:MetaData,
        logger:BaseLogger,
        url:BaseTypes.OptionalString = None
    ):
        self._metadata = metadata #* Define database metadata
        self._logger = logger #* Define database logger

        #* Create engine
        url = url or os.getenv("DB_URL")
        if url is None:
            raise ValueError("DB_URL environment variable must be set if url is not provided")
        self._engine = create_engine(url=url, echo=False, pool_pre_ping=True, pool_recycle=3600)

        self._metadata.create_all(bind=self._engine) #* Create all tables
        self._session = SessionManager(logger=self._logger, engine=self._engine) #* Define session

    def dispose(self) -> None:
        #* Dispose session
        if self._session is not None:
            self._session.dispose()
            self._session = None
        #* Dispose engine
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None
        #* Dispose logger
        if self._logger is not None:
            self._logger.dispose()
            self._logger = None
        #* Dispose metadata
        if self._metadata is not None:
            self._metadata = None