from odoo import models, fields, api, _
from odoo.exceptions import  ValidationError, UserError, Warning


class WizardStartWorkorder(models.TransientModel):
    _name = 'wizard.start.workorder'

    @api.model
    def default_get(self, fields):
        res = super(WizardStartWorkorder, self).default_get(fields)
        active_id = self.env.context.get('active_id') or False
        res['workorder_id'] = active_id
        return res

    workorder_id = fields.Many2one('mrp.workorder', 'Workorder #', readonly=True)
    employee_id = fields.Many2one('hr.employee','Employee', required=True)


    @api.one
    def start_workorder(self):
        mrp_workorder_obj = self.env['mrp.workorder']
        active_id = self.env.context.get('active_id') or False
        mrp_workorder = mrp_workorder_obj.browse(active_id)
        if mrp_workorder:
            mrp_workorder.employee_id = self.employee_id.id
            mrp_workorder.action_
