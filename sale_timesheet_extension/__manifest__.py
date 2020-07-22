# -*- coding: utf-8 -*-
##############################################################################
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################
{
    'name': "Sale Timesheet Extension",

    'summary': """
        This module help to add the project in sale report and also in 
        web view of order.""",

    'description': """
        This module help to add the project in sale report and also in 
        web view of order.
    """,

    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",
    'category': 'Sales',
    'version': "13.0.1.0.3",
    'application': True,
    # any module necessary for this one to work correctly
    'depends': ['sale_timesheet'],
    # always loaded
    'data': [
        'report/sale_report_templates.xml',
        'views/sale_portal_template_view.xml',
        'report/account_invoice_report.xml',
    ],
}
