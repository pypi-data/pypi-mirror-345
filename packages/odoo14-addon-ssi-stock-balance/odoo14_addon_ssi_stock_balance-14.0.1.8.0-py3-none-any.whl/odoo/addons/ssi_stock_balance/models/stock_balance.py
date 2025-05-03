# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from math import ceil

from odoo import _, api, fields, models

from odoo.addons.queue_job.delay import chain
from odoo.addons.ssi_decorator import ssi_decorator


class StockBalance(models.Model):
    _name = "stock_balance"
    _description = "Stock Balance"
    _inherit = [
        "mixin.transaction_queue_cancel",
        "mixin.transaction_queue_done",
        "mixin.transaction_confirm",
        "mixin.transaction_date_duration",
        "mixin.many2one_configurator",
    ]

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "action_queue_done"
    _approval_state = "confirm"
    _after_approved_method = "action_queue_done"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True
    _automatically_insert_multiple_approval_page = True
    _automatically_insert_done_policy_fields = False
    _automatically_insert_done_button = False
    _queue_processing_create_page = True
    _automatically_insert_queue_done_button = False
    _automatically_insert_queue_cancel_button = False

    _queue_to_done_insert_form_element_ok = True
    _queue_to_done_form_xpath = "//group[@name='queue_processing']"

    _queue_to_cancel_insert_form_element_ok = True
    _queue_to_cancel_form_xpath = "//group[@name='queue_processing']"

    _method_to_run_from_wizard = "action_queue_cancel"

    _statusbar_visible_label = "draft,confirm,queue_done,done"
    _policy_field_order = [
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "queue_cancel_ok",
        "cancel_ok",
        "restart_ok",
        "done_ok",
        "queue_done_ok",
        "manual_number_ok",
    ]

    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_reject",
        "dom_queue_done",
        "dom_done",
        "dom_terminate",
        "dom_queue_cancel",
        "dom_cancel",
    ]

    # Sequence attribute
    _create_sequence_state = "done"

    _auto_enqueue_done = False

    type_id = fields.Many2one(
        comodel_name="stock_balance_type",
        string="Type",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    product_ids = fields.Many2many(
        string="Products",
        comodel_name="product.product",
        relation="rel_stock_balance_2_product",
        column1="stock_balance_id",
        column2="product_id",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    product_stock_balance_ids = fields.One2many(
        string="Product Stock Balances",
        comodel_name="product.stock_balance",
        inverse_name="stock_balance_id",
        readonly=True,
    )
    product_stock_balance_warehouse_ids = fields.One2many(
        string="Product Stock Balances - Warehouse",
        comodel_name="product.stock_balance_warehouse",
        inverse_name="sb_id",
        readonly=True,
    )
    product_stock_balance_picking_ids = fields.One2many(
        string="Product Stock Balances - Picking",
        comodel_name="product.stock_balance_picking",
        inverse_name="sb_id",
        readonly=True,
    )
    allowed_product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Allowed Products",
        compute="_compute_allowed_product_ids",
        store=False,
        compute_sudo=True,
    )
    allowed_product_category_ids = fields.Many2many(
        comodel_name="product.category",
        string="Allowed Product Category",
        compute="_compute_allowed_product_category_ids",
        store=False,
        compute_sudo=True,
    )

    @api.depends("type_id")
    def _compute_allowed_product_ids(self):
        for record in self:
            result = False
            if record.type_id:
                result = record._m2o_configurator_get_filter(
                    object_name="product.product",
                    method_selection=record.type_id.product_selection_method,
                    manual_recordset=record.type_id.product_ids,
                    domain=record.type_id.product_domain,
                    python_code=record.type_id.product_python_code,
                )
            record.allowed_product_ids = result

    @api.depends("type_id")
    def _compute_allowed_product_category_ids(self):
        for record in self:
            result = False
            if record.type_id:
                result = record._m2o_configurator_get_filter(
                    object_name="product.category",
                    method_selection=record.type_id.product_category_selection_method,
                    manual_recordset=record.type_id.product_category_ids,
                    domain=record.type_id.product_category_domain,
                    python_code=record.type_id.product_category_python_code,
                )
            record.allowed_product_category_ids = result

    def action_create_product_stock_balance(self):
        for record in self.sudo():
            record._create_product_stock_balance()
            record.product_stock_balance_ids._compute_previous_product_stock_balance_id()

    def action_reload_product(self):
        for record in self.sudo():
            record._reload_product()

    def _reload_product(self):
        self.ensure_one()
        products = self.allowed_product_ids
        Product = self.env["product.product"]
        criteria = [("categ_id.id", "child_of", self.allowed_product_category_ids.ids)]
        products += Product.search(criteria)
        self.write(
            {
                "product_ids": [(6, 0, products.ids)],
            }
        )

    @ssi_decorator.post_queue_done_action()
    def _01_generate_first_level_queue_done(self):
        self.ensure_one()
        product_per_split = 10
        num_split = ceil(len(self.product_ids) / product_per_split)
        latest = False
        for split_number in range(1, num_split + 1):
            if split_number == num_split:
                latest = True
            products = self.product_ids[
                (product_per_split * split_number)
                - product_per_split : split_number * product_per_split
            ]
            description = (
                "Generate first level done queue for stock balance ID %s split number %s"
                % (self.id, split_number)
            )
            self.with_context(job_batch=self.done_queue_job_batch_id).with_delay(
                description=_(description)
            )._generate_second_level_queue_done(products, latest)

    def _generate_second_level_queue_done(self, products, latest):
        self.ensure_one()
        latest_product = False
        for product in products:
            if latest and product == products[-1]:
                latest_product = True
            description = (
                "Generate second level done queue for stock balance ID %s Product %s"
                % (self.id, product.name)
            )
            self.with_context(job_batch=self.done_queue_job_batch_id).with_delay(
                description=_(description)
            )._generate_third_level_queue_done(product, latest_product)

    def _generate_third_level_queue_done(self, product, latest):
        self.ensure_one()
        ProductSB = product_stock_balance = self.env["product.stock_balance"]
        sb_delayables = []
        for stock_balance_date in self._get_date_list():
            product_stock_balance += ProductSB.create(
                {
                    "stock_balance_id": self.id,
                    "product_id": product.id,
                    "date": fields.Date.to_string(stock_balance_date),
                }
            )
        for sb in product_stock_balance:
            description = (
                "Generate third level done queue for stock balance ID %s Product %s Date %s "
                % (self.id, product.name, sb.date)
            )
            current_sb_delayable = (
                self.with_context(job_batch=self.done_queue_job_batch_id)
                .delayable(description=_(description))
                ._generate_final_level_queue_done(sb)
            )
            sb_delayables.append(current_sb_delayable)

        chain(*sb_delayables).delay()
        if latest:
            self.done_queue_job_batch_id.enqueue()

    def _generate_final_level_queue_done(self, sb):
        self.ensure_one()
        sb.action_create_stock_balance_warehouse()
        sb.action_compute_beginning()

    @ssi_decorator.post_queue_cancel_action()
    def _01_delete_product_stock_balance(self):
        self.ensure_one()
        product_per_split = 10
        num_split = ceil(len(self.product_stock_balance_ids) / product_per_split)
        for split_number in range(1, num_split + 1):
            if split_number == num_split:
                pass
            pbs = self.product_stock_balance_ids[
                (product_per_split * split_number)
                - product_per_split : split_number * product_per_split
            ]
            description = "Delete product stock balance for stock balance ID %s" % (
                self.id
            )
            self.with_context(job_batch=self.cancel_queue_job_batch_id).with_delay(
                description=_(description)
            )._delete_product_stock_balance(pbs)

    def _delete_product_stock_balance(self, pbs):
        self.ensure_one()
        pbs.unlink()

    def _get_date_list(self):
        self.ensure_one()
        dates = []
        current_date = fields.Date.to_date(self.date_start)
        date_end = fields.Date.to_date(self.date_end)
        while current_date <= date_end:
            dates.append(current_date)
            current_date = fields.Date.add(current_date, days=1)
        return dates

    def _create_product_stock_balance(self):
        self.ensure_one()
        self.product_stock_balance_ids.unlink()
        ProductSB = self.env["product.stock_balance"]
        for product in self.product_ids:
            for stock_balance_date in self._get_date_list():
                ProductSB.create(
                    {
                        "stock_balance_id": self.id,
                        "product_id": product.id,
                        "date": fields.Date.to_string(stock_balance_date),
                    }
                )

    @api.model
    def _get_policy_field(self):
        res = super(StockBalance, self)._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "cancel_ok",
            "queue_cancel_ok",
            "done_ok",
            "queue_done_ok",
            "reject_ok",
            "restart_ok",
            "restart_approval_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res

    @ssi_decorator.insert_on_form_view()
    def _insert_form_element(self, view_arch):
        if self._automatically_insert_view_element:
            view_arch = self._reconfigure_statusbar_visible(view_arch)
        return view_arch
