{
    'name': 'Purchase Payment Report',
    'version': '19.0.1.0.0',
    'category': 'Purchase',
    'summary': 'Reporte de pagos a proveedores por pedido o por proveedor',
    'author': 'Alphaqueb Consulting',
    'depends': ['purchase', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/purchase_payment_report_wizard_view.xml',
        'report/purchase_payment_report_template.xml',
        'report/purchase_payment_report_action.xml',
        'views/purchase_order_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
