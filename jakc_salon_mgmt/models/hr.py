from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, Warning


class CommissionPeriode(models.Model):
    _name = 'commision.periode'

    name = fields.Date('Date')
    hr_employee_commision_ids = fields.One2many('hr.employee.commision','commision_periode_id','Commisions')
    state = fields.Selection([('open','Open'),('done','Close')])


class HrEmployeeCommision(models.Model):
    _name = 'hr.employee.commision'

    commision_periode_id = fields.Many2one('commision.periode', 'Periode #', readonly=True)
    employee_id = fields.Many2one('hr.employee','Employee', readonly=True)
    sale_order_line_id = fields.Many2one('sale.order.line', 'Sale Order Line', readonly=True)
    mrp_workorder_id = fields.Many2one('mrp.workorder', 'Workorder', readonly=True)
    commision_calculation_method = fields.Selection([('product','Per Product'),('day','Per Day')], 'Calculation Method', readonly=True)
    commision_type = fields.Selection([('fixed','Fixed'),('percentage','Percentage')],'Commision Type', readonly=True)
    amount = fields.Float('Amount', readonly=True, default=0.0)