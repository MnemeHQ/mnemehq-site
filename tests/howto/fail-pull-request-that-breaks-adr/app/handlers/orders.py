from app.repositories.invoices import InvoiceRepository


def list_invoices(customer_id: str):
    return InvoiceRepository().for_customer(customer_id)
