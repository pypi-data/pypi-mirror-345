# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from datetime import datetime, time

import pytz

from odoo import api, fields, models


class ProductStockBalance(models.Model):
    _name = "product.stock_balance"
    _description = "Product Stock Balance"
    _order = "product_id, date asc"

    stock_balance_id = fields.Many2one(
        string="Stock Balances",
        comodel_name="stock_balance",
        required=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
        required=True,
        ondelete="cascade",
    )
    previous_product_stock_balance_id = fields.Many2one(
        string="Previous Stock Balance",
        comodel_name="product.stock_balance",
        compute="_compute_previous_product_stock_balance_id",
        store=True,
    )
    date = fields.Date(
        string="Date",
        required=True,
    )
    qty_beginning = fields.Float(
        string="Beginning Qty.",
        related="previous_product_stock_balance_id.qty_ending",
        store=True,
        compute_sudo=True,
    )
    value_beginning = fields.Float(
        string="Beginning Value",
        related="previous_product_stock_balance_id.value_ending",
        store=True,
        compute_sudo=True,
    )
    qty_in = fields.Float(
        string="In Qty.",
        compute="_compute_qty_in_out",
        store=True,
        compute_sudo=True,
    )
    qty_out = fields.Float(
        string="Out Qty.",
        compute="_compute_qty_in_out",
        store=True,
        compute_sudo=True,
    )
    qty_ending = fields.Float(
        string="Ending Qty.",
        compute="_compute_qty_ending",
        store=True,
        compute_sudo=True,
    )
    value_in = fields.Float(
        string="Value In",
        compute="_compute_qty_in_out",
        store=True,
        compute_sudo=True,
    )
    value_out = fields.Float(
        string="Value Out",
        compute="_compute_qty_in_out",
        store=True,
        compute_sudo=True,
    )
    value_ending = fields.Float(
        string="Ending Value",
        compute="_compute_qty_ending",
        store=True,
        compute_sudo=True,
    )
    stock_move_ids = fields.One2many(
        string="Stock Moves",
        comodel_name="stock.move",
        inverse_name="stock_balance_id",
    )
    stock_balance_warehouse_ids = fields.One2many(
        string="Stock Balance - Warehouse",
        comodel_name="product.stock_balance_warehouse",
        inverse_name="stock_balance_id",
    )

    @api.depends(
        "date",
        "product_id",
    )
    def _compute_previous_product_stock_balance_id(self):
        for record in self:
            result = 0.0
            criteria = [
                ("product_id", "=", record.product_id.id),
                ("date", "<", record.date),
            ]
            datas = self.env["product.stock_balance"].search(criteria)
            if len(datas) >= 1:
                data = datas[-1]
                result = data
            record.previous_product_stock_balance_id = result

    @api.depends(
        "stock_balance_warehouse_ids",
        "stock_balance_warehouse_ids.qty_in",
        "stock_balance_warehouse_ids.qty_out",
        "stock_balance_warehouse_ids.value_in",
        "stock_balance_warehouse_ids.value_out",
    )
    def _compute_qty_in_out(self):
        for record in self:
            qty_in = qty_out = value_in = value_out = 0.0
            for detail in record.stock_balance_warehouse_ids:
                qty_in += detail.qty_in
                qty_out += detail.qty_out
                value_in += detail.value_in
                value_out += detail.value_out
            record.qty_in = qty_in
            record.qty_out = qty_out
            record.value_in = value_in
            record.value_out = value_out

    @api.depends(
        "qty_beginning",
        "value_beginning",
        "qty_in",
        "qty_out",
        "value_in",
        "value_out",
    )
    def _compute_qty_ending(self):
        for record in self:
            qty = record.qty_beginning + record.qty_in - record.qty_out
            value = record.value_beginning + record.value_in - record.value_out
            record.qty_ending = qty
            record.value_ending = value

    def action_create_stock_balance_warehouse(self):
        for record in self.sudo():
            record._create_stock_balance_warehouse()

    def action_compute_beginning(self):
        for record in self.sudo():
            record._compute_beginning()

    def _compute_beginning(self):
        self.ensure_one()
        self._compute_previous_product_stock_balance_id()
        for sb_warehouse in self.stock_balance_warehouse_ids:
            sb_warehouse._compute_previous_product_stock_balance_warehouse_id()
            for sb_picking in sb_warehouse.stock_balance_picking_ids:
                sb_picking._compute_previous_product_stock_balance_picking_id()

    def _create_stock_balance_warehouse(self):
        self.ensure_one()
        for wh in self.env["stock.warehouse"].search([]):
            data = {
                "stock_balance_id": self.id,
                "warehouse_id": wh.id,
            }
            sb_wh = self.env["product.stock_balance_warehouse"].create(data)
            sb_wh.action_create_stock_balance_picking()


class ProductStockBalanceWarehouse(models.Model):
    _name = "product.stock_balance_warehouse"
    _description = "Product Stock Balance - Warehouse"

    stock_balance_id = fields.Many2one(
        string="Product Stock Balance",
        comodel_name="product.stock_balance",
        required=True,
        ondelete="cascade",
    )
    sb_id = fields.Many2one(
        related="stock_balance_id.stock_balance_id",
        store=True,
    )
    previous_product_stock_balance_warehouse_id = fields.Many2one(
        string="Previous Stock Balance Warehouse",
        comodel_name="product.stock_balance_warehouse",
        compute="_compute_previous_product_stock_balance_warehouse_id",
        store=True,
    )
    product_id = fields.Many2one(
        related="stock_balance_id.product_id",
        store=True,
    )
    date = fields.Date(
        related="stock_balance_id.date",
        store=True,
    )
    warehouse_id = fields.Many2one(
        string="Warehouse",
        comodel_name="stock.warehouse",
        required=True,
    )
    qty_beginning = fields.Float(
        string="Qty. Beginning",
        related="previous_product_stock_balance_warehouse_id.qty_ending",
        store=True,
    )
    qty_in = fields.Float(
        string="Qty In",
        compute="_compute_quantity",
        store=True,
        compute_sudo=True,
    )
    qty_out = fields.Float(
        string="Qty In",
        compute="_compute_quantity",
        store=True,
        compute_sudo=True,
    )
    qty_ending = fields.Float(
        string="Ending Qty.",
        compute="_compute_qty_value_ending",
        store=True,
        compute_sudo=True,
    )
    value_beginning = fields.Float(
        string="Value Beginning",
        related="previous_product_stock_balance_warehouse_id.value_ending",
        store=True,
    )
    value_in = fields.Float(
        string="Value In",
        compute="_compute_quantity",
        store=True,
        compute_sudo=True,
    )
    value_out = fields.Float(
        string="Value Out",
        compute="_compute_quantity",
        store=True,
        compute_sudo=True,
    )
    value_ending = fields.Float(
        string="Ending Value",
        compute="_compute_qty_value_ending",
        store=True,
        compute_sudo=True,
    )
    stock_balance_picking_ids = fields.One2many(
        string="Stock Balance - Picking",
        comodel_name="product.stock_balance_picking",
        inverse_name="stock_balance_warehouse_id",
    )

    @api.depends(
        "stock_balance_picking_ids",
        "stock_balance_picking_ids.qty_in",
        "stock_balance_picking_ids.qty_out",
        "stock_balance_picking_ids.value_in",
        "stock_balance_picking_ids.value_out",
    )
    def _compute_quantity(self):
        for record in self:
            qty_in = qty_out = value_in = value_out = 0.0
            for detail in record.stock_balance_picking_ids:
                qty_in += detail.qty_in
                qty_out += detail.qty_out
                value_in += detail.value_in
                value_out += detail.value_out
            record.qty_in = qty_in
            record.qty_out = qty_out
            record.value_in = value_in
            record.value_out = value_out

    @api.depends(
        "date",
        "product_id",
        "warehouse_id",
    )
    def _compute_previous_product_stock_balance_warehouse_id(self):
        for record in self:
            result = False
            criteria = [
                ("product_id", "=", record.product_id.id),
                ("date", "<", record.date),
                ("warehouse_id", "=", record.warehouse_id.id),
            ]
            datas = self.env["product.stock_balance_warehouse"].search(criteria)
            if len(datas) >= 1:
                data = datas[-1]
                result = data
            record.previous_product_stock_balance_warehouse_id = result

    @api.depends(
        "qty_beginning",
        "value_beginning",
        "qty_in",
        "qty_out",
        "value_in",
        "value_out",
    )
    def _compute_qty_value_ending(self):
        for record in self:
            qty = record.qty_beginning + record.qty_in - record.qty_out
            value = record.value_beginning + record.value_in - record.value_out
            record.qty_ending = qty
            record.value_ending = value

    def action_create_stock_balance_picking(self):
        for record in self.sudo():
            record._create_stock_balance_picking()

    def _create_stock_balance_picking(self):
        self.ensure_one()
        criteria = [
            ("warehouse_id", "=", self.warehouse_id.id),
            ("code", "in", ["incoming", "outgoing"]),
        ]
        for picking_type in self.env["stock.picking.type"].search(criteria):
            data = {
                "stock_balance_warehouse_id": self.id,
                "picking_type_id": picking_type.id,
            }
            sb_picking = self.env["product.stock_balance_picking"].create(data)
            sb_picking.action_reload_stock_move()


class ProductStockBalancePicking(models.Model):
    _name = "product.stock_balance_picking"
    _description = "Product Stock Balance - Picking"

    stock_balance_warehouse_id = fields.Many2one(
        string="Stock Balance - Warehouse",
        comodel_name="product.stock_balance_warehouse",
        required=True,
        ondelete="cascade",
    )
    sb_id = fields.Many2one(
        related="stock_balance_warehouse_id.sb_id",
        store=True,
    )
    previous_product_stock_balance_picking_id = fields.Many2one(
        string="Previous Stock Balance Picking",
        comodel_name="product.stock_balance_picking",
        compute="_compute_previous_product_stock_balance_picking_id",
        store=True,
    )
    product_id = fields.Many2one(
        related="stock_balance_warehouse_id.product_id",
        store=True,
    )
    date = fields.Date(
        related="stock_balance_warehouse_id.date",
        store=True,
    )
    picking_type_id = fields.Many2one(
        string="Picking Type",
        comodel_name="stock.picking.type",
        required=True,
        ondelete="restrict",
    )
    warehouse_id = fields.Many2one(
        related="picking_type_id.warehouse_id",
        store=True,
    )
    value_beginning = fields.Float(
        string="Value Beginning",
        related="previous_product_stock_balance_picking_id.value_ending",
        store=True,
    )
    value_in = fields.Float(
        string="Value In",
        compute="_compute_quantity",
        store=True,
    )
    value_out = fields.Float(
        string="Value Out",
        compute="_compute_quantity",
        store=True,
    )
    value_ending = fields.Float(
        string="Ending Value",
        compute="_compute_qty_value_ending",
        store=True,
        compute_sudo=True,
    )
    qty_beginning = fields.Float(
        string="Qty. Beginning",
        related="previous_product_stock_balance_picking_id.qty_ending",
        store=True,
    )
    qty_in = fields.Float(
        string="Qty In",
        compute="_compute_quantity",
        store=True,
    )
    qty_out = fields.Float(
        string="Qty Out",
        compute="_compute_quantity",
        store=True,
    )
    qty_ending = fields.Float(
        string="Ending Qty.",
        compute="_compute_qty_value_ending",
        store=True,
        compute_sudo=True,
    )
    stock_move_ids = fields.One2many(
        string="Stock Moves",
        comodel_name="stock.move",
        inverse_name="stock_balance_picking_id",
    )

    @api.depends(
        "stock_move_ids",
        "stock_move_ids.state",
        "stock_move_ids.product_qty",
        "stock_move_ids.stock_valuation_layer_ids",
        "stock_move_ids.stock_valuation_layer_ids.value",
    )
    def _compute_quantity(self):
        for record in self:
            qty_in = qty_out = qty = 0.0
            value_in = value_out = 0.0
            for move in record.stock_move_ids.filtered(lambda r: r.state == "done"):
                qty = move.product_qty
                if move.picking_type_id.code == "incoming":
                    qty_in += qty
                elif move.picking_type_id.code == "outgoing":
                    qty_out += qty
                for svl in move.stock_valuation_layer_ids.filtered(
                    lambda r: r.account_move_id
                ):
                    if svl.value > 0.0:
                        value_in += svl.value
                    elif svl.value < 0.0:
                        value_out += abs(svl.value)
            record.qty_in = qty_in
            record.qty_out = qty_out
            record.value_in = value_in
            record.value_out = value_out

    @api.depends(
        "date",
        "product_id",
        "picking_type_id",
    )
    def _compute_previous_product_stock_balance_picking_id(self):
        for record in self:
            result = False
            criteria = [
                ("product_id", "=", record.product_id.id),
                ("date", "<", record.date),
                ("picking_type_id", "=", record.picking_type_id.id),
            ]
            datas = self.env["product.stock_balance_picking"].search(criteria)
            if len(datas) >= 1:
                data = datas[-1]
                result = data
            record.previous_product_stock_balance_picking_id = result

    @api.depends(
        "qty_beginning",
        "value_beginning",
        "qty_in",
        "qty_out",
        "value_in",
        "value_out",
    )
    def _compute_qty_value_ending(self):
        for record in self:
            qty = record.qty_beginning + record.qty_in - record.qty_out
            value = record.value_beginning + record.value_in - record.value_out
            record.qty_ending = qty
            record.value_ending = value

    def action_reload_stock_move(self):
        for record in self:
            record._reload_stock_move()

    def _reload_stock_move(self):
        self.ensure_one()

        tz_company = pytz.timezone(self.env.company.partner_id.tz or "UTC")
        tz_utc = pytz.timezone("UTC")
        date_balance = fields.Date.to_date(self.date)
        time_start = time(0, 0, 0)
        time_end = time(23, 59, 59)
        datetime_start = (
            tz_company.localize(datetime.combine(date_balance, time_start))
            .astimezone(tz_utc)
            .strftime("%Y-%m-%d %H:%M:%S")
        )
        datetime_end = (
            tz_company.localize(datetime.combine(date_balance, time_end))
            .astimezone(tz_utc)
            .strftime("%Y-%m-%d %H:%M:%S")
        )

        criteria = [
            ("date", ">=", datetime_start),
            ("date", "<=", datetime_end),
            ("state", "=", "done"),
            ("product_id", "=", self.product_id.id),
            ("stock_balance_picking_id", "=", False),
            ("picking_type_id", "=", self.picking_type_id.id),
        ]
        stock_moves = self.env["stock.move"].search(criteria)
        stock_moves.write(
            {
                "stock_balance_picking_id": self.id,
            }
        )
