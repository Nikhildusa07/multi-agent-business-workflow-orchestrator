from app.database.connection import Base, engine
from app.models import Workflow, Task, AuditLog, Approval


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully!")