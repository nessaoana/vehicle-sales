import os

# src.main builds the real app on import, which requires DATABASE_URL.
os.environ.setdefault("DATABASE_URL", "sqlite://")
