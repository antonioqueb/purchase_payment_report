from odoo import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_purchase_payment_report_from_order(self):
        self.ensure_one()
        # Crea el wizard con los valores fijos y abre la vista simplificada
        wizard = self.env['purchase.payment.report.wizard'].create({
            'report_type': 'order',
            'order_id': self.id,
            'from_order': True,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reporte de Pagos — %s' % self.name,
            'res_model': 'purchase.payment.report.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'views': [(self.env.ref(
                'purchase_payment_report.view_purchase_payment_report_wizard_from_order'
            ).id, 'form')],
            'target': 'new',
        }