# -*- coding: utf-8 -*-
import odoo.exceptions
from odoo import models, fields, api
from odoo.tools import float_utils
from odoo.exceptions import UserError, ValidationError

class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = "Quản lý BĐS"
    _order = "id desc"
    _sql_constraints = [
        ("check_expected_price", "CHECK(expected_price > 0)", "Giá phải dương!"),
        ("check_selling_price", "CHECK(selling_price >= 0)", "Giá bán phải dương!"),
    ]

    name = fields.Char(required=True, default="Unknown")
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(default=lambda self: fields.Datetime.now() + fields.date_utils.relativedelta(months=+3),copy=False)
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True,copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        string='garden_orientation',
        selection=[('north','Bắc'),('south','Nam'),('east',"Đông"),('west',"Tây")],
        help="Xác định hướng xoay của vườn nhà"
    )

    active = fields.Boolean(default=False)
    state = fields.Selection(
        string='states',
        selection=[('new','Mới đăng'),('offer_received','Nhận yêu cầu cọc'), ('offer_accepted','Đã nhận cọc'),('sold','Đã bán'),('cancelled','Đã huỷ')],
        required=True,
        copy=False,
        default='new'
    )

    property_type_id = fields.Many2one("estate.property.type", string="Loại bđs")
    user_id = fields.Many2one("res.users", string="Người bán", default=lambda self: self.env.user)
    buyer_id = fields.Many2one("res.partner", string="Người mua", copy=False, readonly=True)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")

    offer_id = fields.One2many("estate.property.offer","property_id", string="Mặc cả")

    total_area = fields.Integer(
        "Tổng số mét vuông (mv)",
        compute="_cal_total_area",
        help="Cộng diện tích vườn và diện tích nhà",
    )

    best_price = fields.Float(
        string="Giá tốt nhất",
        compute="_cal_best_price"
    )

    @api.depends("garden_area","living_area")
    def _cal_total_area(self):
        for record in self:
            record.total_area += record.living_area + record.garden_area

    @api.depends("offer_id.price")
    def _cal_best_price(self):
        for record in self:
            record.best_price = max(record.offer_id.mapped("price")) if record.offer_id else 0.0
        return max(record.offer_id.mapped("price")) if record.offer_id else 0.0



    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False


    @api.constrains("selling_price")
    def _check_selling_price(self):
        for rec in self:
            if (
                not float_utils.float_is_zero(rec.selling_price, precision_rounding=0.01)
                and float_utils.float_compare(rec.selling_price, rec.expected_price *0.9, precision_rounding=0.01)<0
            ):
                raise ValidationError("Giá bán không được thấp hơn 90% giá mong muốn! Bạn phải hạ giá mong muốn để thoả thuận offer này!")



    @api.ondelete(at_uninstall=False)
    def unlink(self):
        if not set(self.mapped("state")) <= {"new", "canceled"}:
            raise odoo.exceptions.UserError("Chỉ có bđs vừa đăng hoặc bị huỷ mới có thể bị xoá!")
        return super().unlink()


    @api.model
    def create(self, vals):
        vals.update({
            'state':'offer_received'
        })
        return super(EstateProperty,self).create(vals)



    # set State Action
    def set_sold_state(self):
        for rec in self:
            if (rec.state != 'cancelled'):
                rec.state = 'sold'
                rec.buyer_id = rec.offer_id.partner_id

            else:
                raise odoo.exceptions.UserError("Bđs này không thể bán vì đã bị huỷ.")

    def set_cancelled_state(self):
        for rec in self:
            rec.state = 'cancelled'


