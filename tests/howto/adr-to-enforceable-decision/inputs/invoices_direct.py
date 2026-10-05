from app.db.client import get_connection


def list_invoices(customer_id: str):
    conn = get_connection()
    return conn.execute("SELECT * FROM invoices WHERE customer_id = ?", (customer_id,))
