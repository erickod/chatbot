from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    """Base repository class for database operations.

    Provides a common interface for all repository classes with a database session.
    """

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            db_session: SQLAlchemy async database session
        """
        self.db_session: AsyncSession = db_session
