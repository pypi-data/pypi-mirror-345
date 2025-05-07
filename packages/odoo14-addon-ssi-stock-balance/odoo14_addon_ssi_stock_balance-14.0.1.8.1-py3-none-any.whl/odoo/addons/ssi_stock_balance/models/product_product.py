# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pytz

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    stock_balance_ids = fields.One2many(
        string="Stock Balance",
        comodel_name="product.stock_balance",
        inverse_name="product_id",
        readonly=True,
    )
    latest_stock_balance = fields.Date(
        string="Latest Stock Balance",
        compute="_compute_latest_stock_balance",
        store=True,
        compute_sudo=True,
        company_dependent=False,
    )
    first_stock_move_date = fields.Date(
        string="First Stock Move Date",
        compute="_compute_first_stock_move_date",
        store=True,
        compute_sudo=True,
        company_dependent=False,
    )
    stock_balance_picking_ids = fields.One2many(
        string="Stock Balance - Picking",
        comodel_name="product.stock_balance_picking",
        inverse_name="product_id",
    )

    @api.depends(
        "stock_balance_ids",
        "stock_balance_ids.date",
    )
    def _compute_latest_stock_balance(self):
        for record in self:
            result = False
            if len(record.stock_balance_ids) > 0:
                result = record.stock_balance_ids[-1].date
            record.latest_stock_balance = result

    @api.depends(
        "stock_move_ids",
        "stock_move_ids.date",
        "stock_move_ids.state",
    )
    def _compute_first_stock_move_date(self):
        for record in self:
            result = False
            if len(record.stock_move_ids.filtered(lambda r: r.state == "done")) > 0:
                first_sm = record.stock_move_ids.filtered(lambda r: r.state == "done")[
                    0
                ]
                tz_company = pytz.timezone(self.env.company.partner_id.tz or "UTC")
                tz_utc = pytz.timezone("UTC")
                datetime_first = fields.Datetime.to_datetime(first_sm.date)
                result = (
                    tz_company.localize(datetime_first)
                    .astimezone(tz_utc)
                    .strftime("%Y-%m-%d")
                )
            record.first_stock_move_date = result

    def _get_domain_locations(self):
        res = super()._get_domain_locations()
        lot_id = self.env.context.get("lot_id")
        if not lot_id:
            return res

        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = res
        lot_domain = [("forced_lot_id", "=", lot_id)]
        domain_move_in_loc += lot_domain
        domain_move_out_loc += lot_domain
        return domain_quant_loc, domain_move_in_loc, domain_move_out_loc
