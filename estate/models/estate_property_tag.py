from odoo import models, fields

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Property Tag"
    _order = "name"

    # ---------------- FIELDS ----------------
    name = fields.Char(required=True)
    color = fields.Integer()

    # ---------------- SQL CONSTRAINT ----------------
    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'Tag name must be unique')
    ]