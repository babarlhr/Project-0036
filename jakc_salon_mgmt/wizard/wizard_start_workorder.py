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
    user_id = fields.Many2one('res.users','Employee', required=True)


