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


    def _get_account_move_line_values(self):
        move_line_values_by_expense = {}
        for expense in self:
            move_line_name = expense.employee_id.name + ': ' + expense.name.split('\n')[0][:64]
            account_src = expense._get_expense_account_source()
            account_dst = expense._get_expense_account_destination()
            account_date = expense.sheet_id.accounting_date or expense.date or fields.Date.context_today(expense)

            company_currency = expense.company_id.currency_id
            different_currency = expense.currency_id and expense.currency_id != company_currency

            move_line_values = []
            taxes = expense.tax_ids.with_context(round=True).compute_all(expense.unit_amount, expense.currency_id, expense.quantity, expense.product_id)
            total_amount = 0.0
            total_amount_currency = 0.0
            partner_id = expense.employee_id.address_home_id.commercial_partner_id.id

            # source move line
            amount = taxes['total_excluded']
            if expense.markup_value:
                amount = expense.unit_cost
                taxes = expense.tax_ids.with_context(round=True).compute_all(expense.unit_cost, expense.currency_id, expense.quantity, expense.product_id)
            amount_currency = False
            if different_currency:
                amount = expense.currency_id._convert(amount, company_currency, expense.company_id, account_date)
                amount_currency = taxes['total_excluded']
            move_line_src = {
                'name': move_line_name,
                'quantity': expense.quantity or 1,
                'debit': amount if amount > 0 else 0,
                'credit': -amount if amount < 0 else 0,
                'amount_currency': amount_currency if different_currency else 0.0,
                'account_id': account_src.id,
                'product_id': expense.product_id.id,
                'product_uom_id': expense.product_uom_id.id,
                'analytic_account_id': expense.analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)],
                'expense_id': expense.id,
                'partner_id': partner_id,
                'tax_ids': [(6, 0, expense.tax_ids.ids)],
                'tag_ids': [(6, 0, taxes['base_tags'])],
                'currency_id': expense.currency_id.id if different_currency else False,
            }
            move_line_values.append(move_line_src)
            total_amount += -move_line_src['debit'] or move_line_src['credit']
            total_amount_currency += -move_line_src['amount_currency'] if move_line_src['currency_id'] else (-move_line_src['debit'] or move_line_src['credit'])

            # taxes move lines
            for tax in taxes['taxes']:
                amount = tax['amount']
                amount_currency = False
                if different_currency:
                    amount = expense.currency_id._convert(amount, company_currency, expense.company_id, account_date)
                    amount_currency = tax['amount']
                move_line_tax_values = {
                    'name': tax['name'],
                    'quantity': 1,
                    'debit': amount if amount > 0 else 0,
                    'credit': -amount if amount < 0 else 0,
                    'amount_currency': amount_currency if different_currency else 0.0,
                    'account_id': tax['account_id'] or move_line_src['account_id'],
                    'tax_repartition_line_id': tax['tax_repartition_line_id'],
                    'tag_ids': tax['tag_ids'],
                    'tax_base_amount': tax['base'],
                    'expense_id': expense.id,
                    'partner_id': partner_id,
                    'currency_id': expense.currency_id.id if different_currency else False,
                }
                total_amount -= amount
                total_amount_currency -= move_line_tax_values['amount_currency'] or amount
                move_line_values.append(move_line_tax_values)

            # destination move line
            move_line_dst = {
                'name': move_line_name,
                'debit': total_amount > 0 and total_amount,
                'credit': total_amount < 0 and -total_amount,
                'account_id': account_dst,
                'date_maturity': account_date,
                'amount_currency': total_amount_currency if different_currency else 0.0,
                'currency_id': expense.currency_id.id if different_currency else False,
                'expense_id': expense.id,
                'partner_id': partner_id,
            }
            move_line_values.append(move_line_dst)

            move_line_values_by_expense[expense.id] = move_line_values
        return move_line_values_by_expense

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
