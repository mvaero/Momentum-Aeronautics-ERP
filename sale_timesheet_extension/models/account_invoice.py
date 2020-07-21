# -*- encoding: utf-8 -*-
##############################################################################
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_order_id = fields.Many2one('sale.order', 'Sales Order',
                                    compute='_compute_sale_order_id',
                                    store=True, readonly=False)
    project_id = fields.Many2one(
        'project.project', 'Project', related='sale_order_id.project_id')

    def _compute_sale_order_id(self):
        for move in self:
            order_id = move.invoice_line_ids.mapped('sale_line_ids').mapped('order_id')
            if order_id:
                move.sale_order_id = order_id
            else:
                move.sale_order_id = False
