from odoo import models, fields, api, _


class HRExpense(models.Model):
    _inherit = 'hr.expense'

    unit_cost = fields.Monetary('Unit Cost', readonly=True, required=True,
                                states={'draft': [('readonly', False)], 'reported': [('readonly', False)],
                                        'refused': [('readonly', False)]}, digits='Product Price')
    markup_value = fields.Float('Markup(%)')
    project_task = fields.Many2one('project.task', 'Project Task')
    unit_amount = fields.Float("Unit Price", readonly=True, required=True,
                               states={'draft': [('readonly', False)], 'reported': [('readonly', False)],
                                       'refused': [('readonly', False)]}, digits='Product Price',
                               compute="_compute_unit_amount")

    @api.depends('unit_cost', 'markup_value')
    def _compute_unit_amount(self):
        unit_price = 0.0
        if self.unit_cost and self.markup_value:
            unit_price = self.unit_cost + (self.unit_cost * (self.markup_value / 100))
        self.update({'unit_amount': unit_price})


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _sale_prepare_sale_line_values(self, order, price):
        result = super(AccountMoveLine, self)._sale_prepare_sale_line_values(order, price)
        if self.expense_id:
            result.update({
                'price_unit': self.expense_id.unit_amount,
                'product_uom_qty': self.expense_id.quantity
            })
        return result


class ProjectTask(models.Model):
    _inherit = 'project.task'

    expense_count = fields.Integer(compute='_compute_expense_count', string='Number of Generated Leads')
    expense_ids = fields.One2many('hr.expense', 'project_task', string='Expense')

    @api.depends('expense_ids')
    def _compute_expense_count(self):
        for task in self:
            task.expense_count = len(task.expense_ids)

    def action_get_expenses(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.expense",
            "views": [[False, "tree"]],
            'domain': [('id', 'in', self.expense_ids.ids)],
            "context": {"create": False},
        }
