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

    project_name = fields.Char(string="Project",compute='_compute_project_name', help="Show the project namebased on sale order")

    def _compute_project_name(self):
        project_name = ""
        projects = []
        for move in self:
            orders = move.invoice_line_ids.mapped('sale_line_ids').mapped('order_id')
            for order in orders:
                if order.project_id:
                    projects.append(order.project_id.name)
            move.project_name = ','.join(projects)
