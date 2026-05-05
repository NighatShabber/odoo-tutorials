from odoo import api, fields, models
from datetime import timedelta
from odoo.exceptions import UserError, ValidationError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"
    _order = "price desc"

    # ---------------- FIELDS ----------------
    price = fields.Float(required=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline", store=True)
    partner_id = fields.Many2one("res.partner", required=True)

    property_id = fields.Many2one(
        "estate.property",
        required=True,
        ondelete="cascade"
    )
    property_type_id = fields.Many2one(
        "estate.property.type",
        related="property_id.property_type_id",
        store=True
    )
    state = fields.Selection(
        [
            ('accepted', 'Accepted'),
            ('refused', 'Refused')
        ],
        string="Status",
        copy=False,
        default=False
    )

    # ---------------- COMPUTE ----------------
    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date.date() + timedelta(days=record.validity)
            else:
                record.date_deadline = False

    # ---------------- INVERSE ----------------
    def _inverse_date_deadline(self):
        for record in self:
            if record.create_date and record.date_deadline:
                record.validity = (record.date_deadline - record.create_date.date()).days

    # ---------------- CREATE OVERRIDE WITH VALIDATION ----------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            property_id = vals.get('property_id')
            if property_id:
                property_rec = self.env['estate.property'].browse(property_id)
                # Check that the offer price is higher than all existing offers
                existing_offers = property_rec.offer_ids.mapped('price')
                new_price = vals.get('price', 0)
                if existing_offers and max(existing_offers) >= new_price:
                    raise ValidationError("The offer price must be strictly higher than all existing offers.")
                # If property is already sold/accepted/canceled, forbid new offers
                if property_rec.state in ('offer_accepted', 'sold', 'canceled'):
                    raise ValidationError("Cannot create an offer for a property that is already accepted, sold, or canceled.")
        records = super().create(vals_list)
        for record in records:
            if record.property_id and record.property_id.state == 'new':
                record.property_id.state = 'offer_received'
        return records

    # ---------------- ACTIONS ----------------
    def action_accept(self):
        for record in self:
            property_rec = record.property_id
            if property_rec.buyer_id:
                raise UserError("This property already has an accepted offer!")
            # Refuse all other offers for this property
            property_rec.offer_ids.filtered(lambda o: o != record and o.state != 'refused').write({'state': 'refused'})
            property_rec.write({
                'buyer_id': record.partner_id.id,
                'selling_price': record.price,
                'state': 'offer_accepted'
            })
            record.state = 'accepted'
        return True

    def action_refuse(self):
        for record in self:
            record.state = 'refused'
        return True

    # ---------------- SQL CONSTRAINT ----------------
    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)', 'Offer price must be positive')
    ]