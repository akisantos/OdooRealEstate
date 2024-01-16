# -*- coding: utf-8 -*-
from odoo import models, fields

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Property Tag"
    _sql_constraints = [
        ("check_unique_name", "unique(name)", "Hình như tên này có rồi thì phải"),

    ]
    _order = "name desc"
    name = fields.Char(required=True)

    color = fields.Integer()

