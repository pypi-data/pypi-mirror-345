# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockBalanceType(models.Model):
    _name = "stock_balance_type"
    _description = "Stock Balance Type"
    _inherit = [
        "mixin.master_data",
        "mixin.product_product_m2o_configurator",
        "mixin.product_category_m2o_configurator",
    ]

    _product_product_m2o_configurator_insert_form_element_ok = True
    _product_product_m2o_configurator_form_xpath = "//page[@name='product']"
    _product_category_m2o_configurator_insert_form_element_ok = True
    _product_category_m2o_configurator_form_xpath = "//page[@name='product']"

    product_ids = fields.Many2many(
        relation="rel_stock_balance_type_2_product_product",
        column1="stock_balance_type_id",
        column2="product_id",
    )
    product_category_ids = fields.Many2many(
        relation="rel_stock_balance_type_2_product_category",
        column1="stock_balance_type_id",
        column2="product_category_id",
    )
