{
    'name': 'Real Estate Accounting Link',
    'version': '0.1',
    'category': 'Real Estate',
    'summary': 'Generate invoices when a property is sold',
    'description': """
        This module creates an invoice automatically when a real estate property is set to 'Sold'.
        The invoice includes:
        - 6% commission on the selling price
        - €100 administrative fees
    """,
    'author': 'Nighat Shabbir',
    'depends': ['estate', 'account'],
    'data': [],
    'installable': True,
    'application': False,
    'license': 'AGPL-3',
}