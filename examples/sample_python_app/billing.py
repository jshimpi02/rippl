class Customer:
    def __init__(self, name, status, is_premium, age):
        self.name = name
        self.status = status
        self.is_premium = is_premium
        self.age = age


class Invoice:
    def __init__(self, amount):
        self.amount = amount


def calculate_discount(customer, invoice):
    discount = 0
    if customer.is_premium and invoice.amount > 1000:
        discount = invoice.amount * 0.10
    if customer.age >= 65:
        discount += invoice.amount * 0.05
    return discount


def calculate_tax(invoice, state):
    if state == "IL":
        return invoice.amount * 0.1025
    if state == "IN":
        return invoice.amount * 0.07
    return invoice.amount * 0.05


def calculate_total(customer, invoice, state):
    discount = calculate_discount(customer, invoice)
    tax = calculate_tax(invoice, state)
    total = invoice.amount - discount + tax
    if customer.status != "ACTIVE":
        raise ValueError("Inactive customer cannot be billed")
    return total
