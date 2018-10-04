from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, Warning
import logging


logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    barcode = fields.Char('Barcode', size=20)
    hr_employee_job_category_ids = fields.One2many('hr.employee.job.category','employee_id','Commission')


class HrEmployeeJobCategory(models.Model):
    _name = 'hr.employee.job.category'

    employee_id = fields.Many2one('hr.employee','Employee', readonly=True)
    product_job_category_id = fields.Many2one('product.job.category','Category', required=True)
    commission_type_id = fields.Many2one('hr.commission.type','Commission Type', required=True)


class CommissionPeriode(models.Model):
    _name = 'commission.periode'

    @api.one
    def trans_process(self):
        logger.info("Trans Process")
        sale_order_job_employee_obj = self.env['sale.order.job.employee']
        hr_employee_commission_obj = self.env['hr.employee.commission']
        product_job_obj = self.env['product.job']
        product_job_line_obj = self.env['product.job.line']
        args = [('state','=','done')]
        sale_order_job_employee_ids = sale_order_job_employee_obj.search(args)
        logger.info(sale_order_job_employee_ids)
        for sale_order_job_employee_id in sale_order_job_employee_ids:
            sale_order_job_employee_id.state = 'claim'
            commission_values = {}
            commission_values.update({'commission_periode_id': self.id})
            commission_values.update({'employee_id': sale_order_job_employee_id.employee_id.id})
            commission_values.update({'sale_order_id': sale_order_job_employee_id.sale_order_job_id.sale_order_id.id})
            commission_values.update({'sale_order_line_id': sale_order_job_employee_id.sale_order_job_id.sale_order_line_id.id})
            commission_values.update({'sale_order_job_id': sale_order_job_employee_id.sale_order_job_id.id})
            sale_order_job_id = sale_order_job_employee_id.sale_order_job_id
            product_job_id = sale_order_job_id.product_job_id
            product_job_category_id = product_job_id.parent_id
            employee_id = sale_order_job_employee_id.employee_id
            employee_job_category_id = employee_id.hr_employee_job_category_ids.filtered(lambda r: r.product_job_category_id.id == product_job_category_id.id)
            if employee_job_category_id:
                logger.info("Found Employee ")
                logger.info(employee_job_category_id)
                product_job_line_id = product_job_category_id.line_ids.filtered(lambda r: r.commission_type_id.id == employee_job_category_id.commission_type_id.id)
                if product_job_line_id:
                    commission_values.update({'commission_calculation_method': product_job_line_id.commision_calculation_method})
                    commission_values.update({'commission_type': product_job_line_id.commision_calculation_type})
                    if product_job_line_id.commision_calculation_type == 'fixed':
                        amount = product_job_line_id.commision_fixed
                    else:
                        amount = product_job_line_id.commision_fixed
                    commission_values.update({'amount': amount})
                    result = hr_employee_commission_obj.create(commission_values)
                else:
                    result = hr_employee_commission_obj.create(commission_values)
            else:
                result = hr_employee_commission_obj.create(commission_values)



    name = fields.Date('Date')
    hr_employee_commission_ids = fields.One2many('hr.employee.commission','commission_periode_id','Commissions')
    state = fields.Selection([('open','Open'),('done','Close')])


class HrEmployeeCommissionType(models.Model):
    _name = 'hr.commission.type'

    name = fields.Char('Name', size=200, required=True)


class HrEmployeeCommission(models.Model):
    _name = 'hr.employee.commission'

    commission_periode_id = fields.Many2one('commission.periode', 'Periode #', readonly=True)
    employee_id = fields.Many2one('hr.employee','Employee', readonly=True)
    sale_order_id = fields.Many2one('sale.order', 'Sale Order', related='sale_order_line_id.order_id', readonly=True)
    sale_order_line_id = fields.Many2one('sale.order.line', 'Sale Order Line', readonly=True)
    sale_order_job_id = fields.Many2one('sale.order.job', 'Job', readonly=True)
    commission_calculation_method = fields.Selection([('product','Per Product'),('day','Per Day')], 'Calculation Method', readonly=True)
    commission_type = fields.Selection([('fixed','Fixed'),('percentage','Percentage')],'Commission Type', readonly=True)
    amount = fields.Float('Amount', readonly=True, default=0.0)