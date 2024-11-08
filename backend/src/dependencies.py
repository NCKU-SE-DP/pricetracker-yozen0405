from .database import engine, SessionLocal

def session_opener():
    session = SessionLocal(bind=engine)
    try:
        yield session
    finally:
        session.close()