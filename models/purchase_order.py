from odoo import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_purchase_payment_report_from_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reporte de Pagos a Proveedor',
            'res_model': 'purchase.payment.report.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_report_type': 'order',
                'default_order_ids': [(6, 0, [self.id])],
            },
        }
