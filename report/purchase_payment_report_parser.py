from odoo import models


class PurchasePaymentReportParser(models.AbstractModel):
    _name = 'report.purchase_payment_report.report_purchase_payment'
    _description = 'Parser Reporte Pagos Proveedor'

    def _get_report_values(self, docids, data=None):
        # data viene del wizard via report_action(self, data=data)
        return {
            'doc_ids': docids,
            'doc_model': 'purchase.payment.report.wizard',
            'data': data,
        }