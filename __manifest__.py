# __manifest__.py
{
    'name': 'SQL Server Sync',
    'version': '15.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Sync data from SQL Server to Odoo',
    'depends': ['base', 'mail', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        # "views/phieucan.xml",
        # 'views/sync_view.xml',
        # 'data/ir_cron_data.xml',
        'views/device_management_views.xml',
        # "views/menu_items.xml"
    ],
    'installable': True,
    'application': True,
}
