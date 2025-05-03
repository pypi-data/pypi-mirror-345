# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockRule(models.Model):
    _name = "stock.rule"
    _inherit = ["stock.rule"]

    def _get_custom_move_fields(self):
        _super = super(StockRule, self)
        result = _super._get_custom_move_fields()
        result += [
            "to_refund",
            "origin_returned_move_id",
            "purchase_line_id",
        ]
        return result
