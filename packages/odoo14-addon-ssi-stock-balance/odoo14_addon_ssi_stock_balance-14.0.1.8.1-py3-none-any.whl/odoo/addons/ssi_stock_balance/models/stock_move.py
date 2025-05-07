# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, time

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = ["stock.move"]

    stock_balance_id = fields.Many2one(
        string="Stock Balance",
        comodel_name="product.stock_balance",
        ondelete="set null",
    )
    stock_balance_picking_id = fields.Many2one(
        string="Stock Balance",
        comodel_name="product.stock_balance_picking",
        ondelete="set null",
    )

    @api.constrains(
        "state",
        "date",
    )
    def check_latest_stock_balance(self):
        tz_company = pytz.timezone(self.env.company.partner_id.tz or "UTC")
        tz_utc = pytz.timezone("UTC")
        for record in self.sudo():
            if record.state != "done" or (
                record._origin.state != "done" and record.state == "cancel"
            ):
                return True

            latest_date = record.product_id.latest_stock_balance

            if not latest_date:
                return True

            date_balance = fields.Date.to_date(latest_date)
            time_balance = time(23, 59, 59)
            datetime_start = (
                tz_company.localize(datetime.combine(date_balance, time_balance))
                .astimezone(tz_utc)
                .replace(tzinfo=None)
            )

            if record.date <= datetime_start:
                error_message = """
                    Document Type: %s
                    Context: Finish document
                    Database ID: %s
                    Problem: Date of transfer before product's (%s) latest stock balance
                    Solution: Adjust actual movement date or cancel stock balance
                    """ % (
                    record._description.lower(),
                    record.id,
                    record.product_id.name,
                )
                raise UserError(_(error_message))
