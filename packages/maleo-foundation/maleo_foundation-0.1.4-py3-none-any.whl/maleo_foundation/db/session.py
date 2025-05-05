from contextlib import contextmanager
from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Generator, Optional
from maleo_foundation.utils.logger import BaseLogger

class SessionManager:
    _logger:Optional[BaseLogger] = None
    _sessionmaker:Optional[sessionmaker[Session]] = None

    @classmethod
    def initialize(cls, logger:BaseLogger, engine:Engine) -> None:
        """Initialize the sessionmaker if not already initialized."""
        if cls._sessionmaker is None:
            cls._logger = logger
            cls._sessionmaker = sessionmaker(bind=engine, expire_on_commit=False)
            cls._logger.info("SessionManager initialized successfully.")

    @classmethod
    def _session_handler(cls) -> Generator[Session, None, None]:
        """Reusable function for managing database sessions."""
        if cls._logger is None:
            raise RuntimeError("Logger has not been initialized. Call initialize() first.")
        if cls._sessionmaker is None:
            raise RuntimeError("SessionLocal has not been initialized. Call initialize() first.")

        session = cls._sessionmaker()
        cls._logger.debug("New database session created.")
        try:
            yield session  #* Provide session
            session.commit()  #* Auto-commit on success
        except SQLAlchemyError as e:
            session.rollback()  #* Rollback on error
            cls._logger.error(f"[SQLAlchemyError] Database transaction failed: {e}", exc_info=True)
            raise
        except Exception as e:
            session.rollback()  #* Rollback on error
            cls._logger.error(f"[Exception] Database transaction failed: {e}", exc_info=True)
            raise
        finally:
            session.close()  #* Ensure session closes
            cls._logger.debug("Database session closed.")

    @classmethod
    def inject(cls) -> Generator[Session, None, None]:
        """Returns a generator that yields a SQLAlchemy session for dependency injection."""
        return cls._session_handler()

    @classmethod
    @contextmanager
    def get(cls) -> Generator[Session, None, None]:
        """Context manager for manual session handling. Supports `with SessionManager.get() as session:`"""
        yield from cls._session_handler()

    @classmethod
    def dispose(cls) -> None:
        """Dispose of the sessionmaker and release any resources."""
        if cls._sessionmaker is not None:
            cls._sessionmaker.close_all()
            cls._sessionmaker = None

        cls._logger.info("SessionManager disposed successfully.")
        cls._logger = None

class SessionManagerV2:
    def __init__(self, logger:BaseLogger, sessionmaker:sessionmaker[Session]):
        self._logger = logger
        self._sessionmaker = sessionmaker

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