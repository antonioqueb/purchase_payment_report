from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchasePaymentReportWizard(models.TransientModel):
    _name = 'purchase.payment.report.wizard'
    _description = 'Asistente Reporte de Pagos a Proveedor'

    report_type = fields.Selection([
        ('partner', 'Por Proveedor'),
        ('order', 'Por Pedido'),
    ], string='Tipo de Reporte', required=True, default='partner')

    partner_id = fields.Many2one(
        'res.partner', string='Proveedor',
        domain=[('supplier_rank', '>', 0)],
    )
    order_ids = fields.Many2many(
        'purchase.order', string='Pedidos de Compra',
        domain=[('state', 'in', ['purchase', 'done'])],
    )
    date_from = fields.Date(string='Fecha Desde')
    date_to = fields.Date(string='Fecha Hasta')

    @api.onchange('report_type')
    def _onchange_report_type(self):
        self.partner_id = False
        self.order_ids = [(5, 0, 0)]

    def action_print_report(self):
        self.ensure_one()
        data = self._prepare_report_data()
        if not data['orders']:
            raise UserError(_('No se encontraron pedidos de compra con los filtros seleccionados.'))
        return self.env.ref('purchase_payment_report.action_purchase_payment_report').report_action(self, data=data)

    def _prepare_report_data(self):
        domain = [('state', 'in', ['purchase', 'done'])]

        if self.report_type == 'partner':
            if not self.partner_id:
                raise UserError(_('Debe seleccionar un proveedor.'))
            domain.append(('partner_id', '=', self.partner_id.id))
        else:
            if not self.order_ids:
                raise UserError(_('Debe seleccionar al menos un pedido.'))
            domain.append(('id', 'in', self.order_ids.ids))

        if self.date_from:
            domain.append(('date_order', '>=', self.date_from))
        if self.date_to:
            domain.append(('date_order', '<=', self.date_to))

        orders = self.env['purchase.order'].search(domain, order='date_order asc')
        orders_data = []

        for order in orders:
            currency = order.currency_id
            amount_total = order.amount_total

            # Pagos realizados: facturas validadas asociadas al pedido
            invoices = order.invoice_ids.filtered(lambda i: i.state == 'posted' and i.move_type == 'in_invoice')
            credit_notes = order.invoice_ids.filtered(lambda i: i.state == 'posted' and i.move_type == 'in_refund')

            amount_invoiced = sum(invoices.mapped('amount_total_signed')) - sum(credit_notes.mapped('amount_total_signed'))
            amount_paid = 0.0

            for inv in invoices:
                for payment in inv._get_reconciled_payments():
                    # Convertir a la divisa del pedido si es necesario
                    if payment.currency_id == currency:
                        amount_paid += payment.amount
                    else:
                        amount_paid += payment.currency_id._convert(
                            payment.amount, currency,
                            order.company_id, payment.date
                        )

            for cn in credit_notes:
                for payment in cn._get_reconciled_payments():
                    if payment.currency_id == currency:
                        amount_paid -= payment.amount
                    else:
                        amount_paid -= payment.currency_id._convert(
                            payment.amount, currency,
                            order.company_id, payment.date
                        )

            # Saldo pendiente = total del pedido - lo pagado
            # Usamos residual de facturas para mayor precisión
            amount_residual = sum(invoices.mapped('amount_residual')) - sum(credit_notes.mapped('amount_residual'))

            # Si no hay facturas, todo el pedido está pendiente
            if not invoices:
                amount_paid = 0.0
                amount_residual = amount_total

            orders_data.append({
                'name': order.name,
                'partner_name': order.partner_id.name,
                'date_order': order.date_order.strftime('%d/%m/%Y') if order.date_order else '',
                'currency_name': currency.name,
                'currency_symbol': currency.symbol,
                'amount_total': amount_total,
                'amount_paid': amount_paid,
                'amount_residual': amount_residual,
                'state': dict(order._fields['state'].selection).get(order.state, order.state),
                'invoice_count': len(invoices),
            })

        # Agrupar por proveedor para el reporte por proveedor
        report_title = ''
        if self.report_type == 'partner':
            report_title = self.partner_id.name
        else:
            report_title = 'Pedidos Seleccionados'

        return {
            'report_type': self.report_type,
            'report_title': report_title,
            'date_from': self.date_from.strftime('%d/%m/%Y') if self.date_from else '',
            'date_to': self.date_to.strftime('%d/%m/%Y') if self.date_to else '',
            'orders': orders_data,
            'company_name': self.env.company.name,
            'company_vat': self.env.company.vat or '',
        }
