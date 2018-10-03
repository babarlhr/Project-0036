from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, Warning
from datetime import datetime


class ProductCategory(models.Model):
    _inherit = 'product.category'

    line_ids = fields.One2many('product.job.line','product_category_id','Jobs')


class ProductJobCategory(models.Model):
    _name = 'product.job.category'

    name = fields.Char('Name', size=200, required=True)
    job_line_ids = fields.One2many('product.job', 'parent_id', 'Product Jobs')
    line_ids = fields.One2many('product.job.line', 'product_job_category_id', 'Jobs')


class ProductJob(models.Model):
    _name = 'product.job'
    name = fields.Char('Name', size=200, required=True)
    parent_id = fields.Many2one('product.job.category','Category')
    line_ids = fields.One2many('product.job.line','product_job_id','Jobs')


class ProductJobLine(models.Model):
    _name = 'product.job.line'

    @api.one
    def get_state(self):
        if datetime.strptime(self.date_start,'%Y-%m-%d') <= datetime.today() and datetime.strptime(self.date_end,'%Y-%m-%d') >= datetime.today():
            self.state = 'open'
        else:
            self.state = 'done'

    product_category_id = fields.Many2one('product.category','Product Category', readonly=True)
    product_job_category_id = fields.Many2one('product.job.category', readonly=True)
    product_job_id = fields.Many2one("product.job",'Product Job', readonly=True)
    commission_type_id = fields.Many2one('hr.commission.type', 'Commission Type')
    company_id = fields.Many2one('res.company', 'Company', required=True)
    date_start = fields.Date('Start Date', required=True)
    date_end = fields.Date('End Date', required=True)
    commision_calculation_method = fields.Selection([('product', 'Per Product'), ('day', 'Per Day')],
                                                    'Calculation Method', default='product', required=True)
    commision_calculation_type = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')],
                                                  'Caclculation Type', default='fixed', required=True)
    commision_fixed = fields.Float('Fixed Amount', default=0.0)
    commision_percentage = fields.Float('Percentage', default=0.0)
    state = fields.Selection([('open', 'Open'), ('done', 'Close')], 'Status', compute="get_state", readonly=True)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    type = fields.Selection(selection_add=[('packet', 'Packet Product')])
    packet_product_id = fields.Many2one('product.product', 'Packet Product')
    packet_product_uom = fields.Many2one('product.uom', 'Packet Uom')
    packet_product_uom_qty = fields.Float('Qty', default=1)
    product_template_job_ids = fields.One2many('product.template.job','product_template_id', 'Jobs')
    product_template_pack_ids = fields.One2many('product.template.pack', 'product_template_id', 'Packs')
    product_template_employee_ids = fields.One2many('product.template.employee','product_template_id', 'Employees')


class ProductTemplateJob(models.Model):
    _name = 'product.template.job'

    product_template_id = fields.Many2one('product.template','Product')
    name = fields.Many2one('product.job', 'Product Job', required=True)
    sequence = fields.Integer('Sequence', required=True)
    iface_commission_fee = fields.Boolean('Commission Fee', default=True)


class ProducTemplatePack(models.Model):
    _name = 'product.template.pack'

    product_template_id = fields.Many2one('product.template','Product')
    product_id = fields.Many2one('product.template','Product', required=True)
    product_uom = fields.Many2one('product.uom','Uom', required=True)
    product_uom_qty = fields.Float('Qty', default=1)
    iface_mandatory = fields.Boolean('Mandatory', default=True)


class ProductTemplateEmployee(models.Model):
    _name = 'product.template.employee'

    @api.one
    def get_state(self):
        if datetime.strptime(self.date_start,'%Y-%m-%d') <= datetime.today() and datetime.strptime(self.date_end,'%Y-%m-%d') >= datetime.today():
            self.state = 'open'
        else:
            self.state = 'done'

    product_template_id = fields.Many2one('product.template','Product')
    employee_id = fields.Many2one('hr.employee','Employee')
    company_id = fields.Many2one('res.company','Company', required=True)
    list_price = fields.Float('Sale Price', default=0.0, required=True)
    date_start = fields.Date('Start Date', required=True)
    date_end = fields.Date('End Date', required=True)
    state = fields.Selection([('open','Open'),('done','Close')] ,'Status', compute="get_state", readonly=True)

