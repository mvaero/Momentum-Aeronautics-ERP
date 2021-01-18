# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class SaleOrderLine(models.Model):
    """Update Analytic Account in procurment."""

    _inherit = 'sale.order.line'

    def _prepare_procurement_values(self, group_id=False):
        """Update Analytic Account in Procurment.

        Prepare specific key for moves or other components that will be
        created from a stock rule comming from a sale order line.
        This method could be override in order to add other custom key that
        could be used in move/po creation.
        """
        values = super(
            SaleOrderLine, self)._prepare_procurement_values(group_id)
        self.ensure_one()
        values.update({
            'account_analytic_id': self.order_id.analytic_account_id.id
        })
        return values
