from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, Warning
from random import random, randint


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    iface_stylist = fields.Boolean('Stylist Here', default=False)


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def _random_with_N_digits(self, number_digit):
        range_start = 10 ** (number_digit - 1)
        range_end = (10 ** number_digit) - 1
        return randint(range_start, range_end)

    iface_stylist = fields.Boolean('Stylist Here', default=False, readonly=True)
    barcode = fields.Char('Barcode', size=20)
    employee_id = fields.Many2one('hr.employee', 'Responsible')
    employee_commision_id = fields.Many2one('hr.employee.commision','Commision', readonly=True)


    @api.model
    def create(self, vals):
        barcode = self._random_with_N_digits()
        vals.update({'barcode', barcode})
        return super(MrpWorkorder, self).create(vals)


class MrpWorkcenterProductivity(models.Model):
    _inherit = 'mrp.workcenter.productivity'

    employee_id = fields.Many2one('hr.employee','Employee')
