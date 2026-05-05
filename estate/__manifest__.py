{
    'name': "Real Estate",
    'summary': "Real Estate Management Module",
    'description': "Complete real estate module for property management.",
    'author': "Nighat Shabbir",
    'category': 'Real Estate/Brokerage',
    'version': '0.1',
    'application': True,
    'installable': True,
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'security/estate_record_rules.xml',
        'views/estate_property_views.xml',
    ],
    'license': 'AGPL-3',
}