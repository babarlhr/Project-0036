from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, Warning


class WizardWorkorderBarcode(models.TransientModel):
    _name = 'wizard.workorder.barcode'

    @api.onchange('barcode')
    def onchange_barcode(self):
        mrp_workorder_obj = self.env['mrp.workorder']
        args = [('barcode', '=', self.barcode)]
        mrp_workorder_id = mrp_workorder_obj.search(args, limit=1)
        if mrp_workorder_id:
            self.workorder_id = mrp_workorder_id.id
        else:
            raise ValidationError("Barcode not Found")

    barcode = fields.Char('Barcode', size=20, required=True)
    workorder_id = fields.Many2one('mrp.workorder','Workorder', readonly=True)
    employee_id = fields.Many2one('hr.employee','Employee', required=True)

    @api.one
    def process_barcode(self):
        print "Proces Absence"
        mrp_workorder_obj = self.env['mrp.workorder']
        args = [('barcode', '=', self.barcode)]
        mrp_workorder_id = mrp_workorder_obj.search(args, limit=1)
        if mrp_workorder_id:
            mrp_workorder_id.employee_id = self.employee_id.id


