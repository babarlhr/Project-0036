from odoo import models, fields, api, _
from odoo.exceptions import  ValidationError, UserError, Warning


class WizardAddWorkorderEmployee(models.TransientModel):
    _name = 'wizard.add.workorder.employee'

    @api.model
    def default_get(self, fields):
        res = super(WizardAddWorkorderEmployee, self).default_get(fields)
        active_id = self.env.context.get('active_id') or False
        res['sale_job_id'] = active_id
        return res

    sale_job_id = fields.Many2one('sale.order.job', 'Workorder #', readonly=True)
    employee_id = fields.Many2one('hr.employee','Employee', required=True)

    @api.one
    def add_workorder_employee(self):
        sale_order_job_obj = self.env['sale.order.job']
        sale_order_job_employee_obj = self.env['sale.order.job.employee']
        active_id = self.env.context.get('active_id') or False
        sale_order_job_id = sale_order_job_obj.browse(active_id)
        if sale_order_job_id:
            is_exist = False
            for job_employee_id in sale_order_job_id.job_employee_ids:
                if job_employee_id.employee_id.id == self.employee_id.id:
                    is_exist = True
                    break
            if is_exist:
                raise ValidationError("Employee Already register on job")
            else:
                values = {}
                values.update({'sale_order_job_id': sale_order_job_id.id})
                values.update({'employee_id': self.employee_id.id})
                result = sale_order_job_employee_obj.create(values)
