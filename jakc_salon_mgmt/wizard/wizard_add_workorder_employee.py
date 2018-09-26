from odoo import models, fields, api, _
from odoo.exceptions import  ValidationError, UserError, Warning


class WizardAddWorkorderEmployee(models.TransientModel):
    _name = 'wizard.add.workorder.employee'

    @api.model
    def default_get(self, fields):
        res = super(WizardAddWorkorderEmployee, self).default_get(fields)
        active_id = self.env.context.get('active_id') or False
        res['workorder_id'] = active_id
        return res

    workorder_id = fields.Many2one('mrp.workorder', 'Workorder #', readonly=True)
    employee_id = fields.Many2one('hr.employee','Employee', required=True)
