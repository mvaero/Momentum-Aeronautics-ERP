# -*- encoding: utf-8 -*-
##############################################################################
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2016 (http://www.bistasolutions.com)
#
##############################################################################
{
    'name': 'Project Task Expense',
    'version': '13.1.0',
    'category': 'Task Expense',
    'author': 'Bista Solutions',
    'description': """
     """,
    'website': 'https://www.bistasolutions.com/',
    'depends': [
        'hr_expense',
        'sale_expense',
    ],
    'data': [
        'views/task_expense_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
