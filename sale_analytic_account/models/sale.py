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


class SaleOrder(models.Model):
    """Create Analytic before procument run."""

    _inherit = 'sale.order'

    def _action_confirm(self):
        """Create Analytic before confirm.

        Implementation of additionnal mecanism of Sales Order confirmation.
        This method should be extended when the confirmation should
        generated other documents. In this method, the SO are in 'sale'
        state (not yet 'done').
        """
        # create an analytic account if at least an expense product
        for order in self:
            if any([expense_policy not in [False, 'no'] for expense_policy in
                    order.order_line.mapped('product_id.expense_policy')]):
                if not order.analytic_account_id:
                    order._create_analytic_account()

        return super(SaleOrder, self)._action_confirm()
