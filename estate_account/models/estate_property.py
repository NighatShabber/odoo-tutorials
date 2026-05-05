from odoo import api, fields, models, _
from odoo import Command
from odoo.exceptions import UserError, AccessError

class EstateProperty(models.Model):
    _inherit = "estate.property"

    def action_sold(self):
        # Explicit security check: ensure current user can update this property
        for record in self:
            try:
                record.check_access('write')   # raises AccessError if not allowed
            except AccessError:
                raise UserError(_("You are not allowed to confirm the sale of this property."))

        # Call original to change state (will also trigger any other logic)
        res = super().action_sold()

        for record in self:
            if record.selling_price <= 0:
                raise UserError(_("Cannot invoice: selling price is not set or zero."))
            if not record.buyer_id:
                raise UserError(_("Cannot invoice: no buyer assigned to this property."))

            journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
            if not journal:
                raise UserError(_("No sales journal found. Please configure accounting."))

            # Prepare invoice values
            invoice_vals = {
                'partner_id': record.buyer_id.id,
                'move_type': 'out_invoice',
                'journal_id': journal.id,
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': [
                    Command.create({
                        'name': f"Commission {record.selling_price} * 6%",
                        'quantity': 1,
                        'price_unit': record.selling_price * 0.06,
                    }),
                    Command.create({
                        'name': "Administrative fees",
                        'quantity': 1,
                        'price_unit': 100.00,
                    }),
                ],
            }

            # Create invoice with sudo() to bypass access rights/record rules
            invoice = self.env['account.move'].sudo().create(invoice_vals)

            record.message_post(body=_("Invoice %(invoice_name)s has been created for the sale of this property.",
                                       invoice_name=invoice.name))

        return res