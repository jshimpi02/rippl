from billing import Customer, Invoice, calculate_total


def create_invoice_response(customer_name, status, is_premium, age, amount, state):
    customer = Customer(customer_name, status, is_premium, age)
    invoice = Invoice(amount)
    total = calculate_total(customer, invoice, state)
    return {"customer": customer.name, "total": total}
