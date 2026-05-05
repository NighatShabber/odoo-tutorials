from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError
from odoo.tools.float_utils import float_compare




class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"
    _order = "id desc"

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )


    # ---------------- BASIC FIELDS ----------------
    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()

    date_availability = fields.Date(
        copy=False,
        default=lambda self: fields.Date.today() + timedelta(days=90)
    )

    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()

    # ---------------- GARDEN FIELDS ----------------
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West')
    ])

    # ---------------- OTHER FIELDS ----------------
    active = fields.Boolean(default=True)

    state = fields.Selection(
        [
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Canceled')
        ],
        required=True,
        copy=False,
        default='new'
    )

    # ---------------- RELATIONS ----------------
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    salesperson_id = fields.Many2one(
        "res.users",
        string="Salesperson",
        default=lambda self: self.env.user
    )
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    # ---------------- COMPUTED FIELDS ----------------
    total_area = fields.Float(compute="_compute_total_area", store=True)
    best_price = fields.Float(string="Best Offer", compute="_compute_best_price", store=True)

    # ---------------- COMPUTE METHODS ----------------
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = (record.living_area or 0) + (record.garden_area or 0)

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            prices = record.offer_ids.mapped("price")
            record.best_price = max(prices) if prices else 0.0

    # ---------------- ONCHANGE ----------------
    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            if not self.garden_area:
                self.garden_area = 10
            if not self.garden_orientation:
                self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    # ---------------- ACTION BUTTONS ----------------
    def action_cancel(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("Sold property cannot be canceled!")
            record.state = 'canceled'

    def action_sold(self):
        for record in self:
            if record.state == 'canceled':
                raise UserError("Canceled property cannot be sold!")
            record.state = 'sold'

    # ---------------- ON DELETE ----------------
    @api.ondelete(at_uninstall=False)
    def _check_on_delete(self):
        for record in self:
            if record.state not in ('new', 'canceled'):
                raise UserError("Only properties in 'New' or 'Canceled' state can be deleted.")

    # ---------------- CONSTRAINTS ----------------
    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            if record.selling_price > 0:
                min_price = record.expected_price * 0.9
                if float_compare(record.selling_price, min_price, precision_digits=2) < 0:
                    raise ValidationError("Selling price cannot be less than 90% of expected price")




    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)', 'Expected price must be positive'),
        ('check_selling_price', 'CHECK(selling_price >= 0)', 'Selling price must be positive')
    ]