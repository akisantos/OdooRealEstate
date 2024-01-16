# -*- coding: utf-8 -*-
import odoo.exceptions
from odoo import models, fields,api

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Property Offer"
    _sql_constraints = [
        ("check_price", "CHECK(price > 0)", "Giá phải dương :v"),
    ]
    _order = "price desc"
    price = fields.Float(string="Giá đề xuất")
    status = fields.Selection(
        copy=False,
        selection=[('accepted','Chấp thuận'),('refused','Từ chối')],
        string="Trạng thái"
    )
    partner_id = fields.Many2one("res.partner", required=True, string="Khách")
    property_id = fields.Many2one("estate.property", required=True)
    validity = fields.Integer(default=1)
    date_deadline = fields.Date(compute="_cal_date_deadline", inverse="_inverse_date_deadline")

    property_type_id = fields.Many2one("estate.property.type",related="property_id.property_type_id", store=True, string="Property Type")

    @api.depends("validity","create_date")
    def _cal_date_deadline(self):
        for rec in self:
            date = rec.create_date.date() if rec.create_date else fields.Date.today()
            rec.date_deadline = date + fields.date_utils.relativedelta(days=rec.validity)

    def _inverse_date_deadline(self):
        for rec in self:
            date = rec.create_date.date() if rec.create_date else fields.Date.today()
            rec.validity = (rec.date_deadline - date).days


    def offer_accept(self):
        if "accepted" in self.mapped("property_id.offer_id.status"):
            raise odoo.exceptions.UserError("Bđs này đã được thoả thuận với người mua khác")

        self.write({
            'status': 'accepted',
        })
        return self.mapped("property_id").write({
            "state": "offer_accepted",
            "buyer_id": self.partner_id.id,
            "selling_price": self.price
        })

    def offer_refuse(self):
        return self.write({
            'status': 'refused'
        })


    @api.model
    def create(self, vals):
        bestprice = self.env['estate.property'].browse(vals['property_id'])._cal_best_price()
        print(vals)
        if (vals['price'] < bestprice):
            raise odoo.exceptions.ValidationError("Đã có người trả giá cao hơn bạn! Hãy thêm tiền vào để cao hơn " + bestprice + "!")
        return super(EstatePropertyOffer,self).create(vals)