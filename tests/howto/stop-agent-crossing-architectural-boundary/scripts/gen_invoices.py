from pathlib import Path

Path("app/handlers").mkdir(parents=True, exist_ok=True)
Path("app/handlers/invoices.py").write_text("from app.db.client import get_connection\n")
