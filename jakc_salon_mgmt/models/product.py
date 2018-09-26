from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, Warning


class ProductTemplateEmployee(models.Model):
    _name = 'product.template.employee'

    product_template_id = fields.Many2one('product.template','Product')
    employee_id = fields.Many2one('hr.employee','Employee', required=True)
    company_id = fields.Many2one('res.company','Company', required=True)
    list_price = fields.Float('Sale Price', default=0.0, required=True)
    commision_calculation_method = fields.Selection([('product','Per Product'),('day','Per Day')], 'Calculation Method', default='product', required=True)
    commision_type = fields.Selection([('fixed','Fixed'),('percentage','Percentage')],'Commision Type', default='fixed', required=True)
    commision_fixed = fields.Float('Fixed Amount', default=0.0)
    commision_percentage = fields.Float('Percentage', default=0.0)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_template_employee_ids = fields.One2many('product.template.employee','product_template_id', 'Employees')