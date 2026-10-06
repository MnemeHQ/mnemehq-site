import app.db.client as db


def list_invoices(customer_id: str):
    return db.get_connection().execute("SELECT * FROM invoices")
