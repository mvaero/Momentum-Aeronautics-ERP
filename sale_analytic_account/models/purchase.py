# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class StockRule(models.Model):
    """Update analytic account in POL."""

    _inherit = 'stock.rule'

    @api.model
    def _prepare_purchase_order_line(self, product_id, product_qty,
                                     product_uom, company_id, values, po):
        res = super(StockRule, self)._prepare_purchase_order_line(
            product_id, product_qty, product_uom, company_id, values, po)
        res['account_analytic_id'] = values.get(
            'account_analytic_id', False) and values.get(
            'account_analytic_id').id
        return res

    def _update_purchase_order_line(self, product_id, product_qty, product_uom,
                                    company_id, values, line):
        res = super(StockRule, self)._update_purchase_order_line(
            product_id, product_qty, product_uom, company_id, values, line)
        res['account_analytic_id'] = values.get(
            'account_analytic_id', False) and values.get(
            'account_analytic_id').id
        return res


class StockMove(models.Model):
    """Update analytic account in POL."""

    _inherit = "stock.move"

    def _prepare_procurement_values(self):
        """Create or Merge PO if MTO route find.

        Prepare specific key for moves or other componenets that will be
        created from a stock rule comming from a stock move.
        This method could be override in order to add other custom key that
        could be used in move/po creation.
        """
        values = super(StockMove, self)._prepare_procurement_values()
        values.update(
            {'account_analytic_id':
             self.sale_line_id.order_id.analytic_account_id})
        return values
