from odoo import models, fields, api, _
from odoo.exceptions import  ValidationError, UserError, Warning
from random import randint

import logging


logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        for order in self:
            order.state = 'sale'
            order.confirmation_date = fields.Datetime.now()
            if self.env.context.get('send_email'):
                self.force_quotation_send()
            order.order_line._action_procurement_create()
            order.order_line._action_salon_create()
        if self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting'):
            self.action_done()
        return True

    @api.multi
    def action_done(self):
        self._action_salon_finish()
        return self.write({'state': 'done'})

    @api.multi
    def _action_salon_finish(self):
        # Create Stock Picking
        stock_picking_obj = self.env['stock.picking']
        stock_move_obj = self.env['stock.move']
        warehouse_id = self.warehouse_id
        out_type_id = warehouse_id.out_type_id
        picking_vals = {}
        picking_vals.update({'sale_id': self.id})
        picking_vals.update({'partner_id': self.partner_id.id})
        picking_vals.update({'location_id': out_type_id.default_location_src_id.id})
        picking_vals.update({'location_dest_id': out_type_id.default_location_src_id.id})
        picking_vals.update({'move_type': 'direct'})
        picking_vals.update({'picking_type_id': out_type_id.id})
        picking_vals.update({'priority': '1'})
        stock_picking_id = stock_picking_obj.create(picking_vals)
        if stock_picking_id:
            for pack_id in self.pack_ids:
                stock_move_id = stock_move_obj.create({
                    'name': self.name,
                    'picking_id': stock_picking_id.id,
                    'product_id': pack_id.product_id.id,
                    'restrict_lot_id': False,
                    'product_uom_qty': pack_id.product_uom_qty,
                    'product_uom': pack_id.product_uom.id,
                    'partner_id': self.partner_id.id,
                    'location_id': out_type_id.default_location_src_id.id,
                    'location_dest_id': out_type_id.default_location_dest_id.id,
                })
                pack_id.write({'stock_picking_id': stock_picking_id.id, 'stock_move_id': stock_move_id.id})
            stock_picking_id.action_done()
        else:
            raise ValidationError('Error Create Stock Picking')



    production_ids = fields.One2many('mrp.production','sale_id', 'Productions', readonly=True)
    workorder_ids = fields.One2many('mrp.workorder','sale_id','Work Orders', readonly=True)
    pack_ids = fields.One2many('sale.order.pack','sale_order_id', 'Packs', readonly=False)
    job_ids = fields.One2many('sale.order.job','sale_order_id','Jobs', readonly=False)


class SalesOrderLine(models.Model):
    _inherit = 'sale.order.line'


    @api.multi
    def _action_salon_create(self):
        logger.info("Action Salon Create")
        sale_order_pack_obj = self.env['sale.order.pack']
        sale_order_job_obj = self.env['sale.order.job']
        for line in self:
            sale_order_id = line.order_id
            product_template_id = line.product_id.product_tmpl_id
            if product_template_id.type == 'service':
                if not line.order_id.procurement_group_id:
                    vals = line.order_id._prepare_procurement_group()
                    line.order_id.procurement_group_id = self.env["procurement.group"].create(vals)
                for pack_id in product_template_id.product_template_pack_ids:
                    pack_values = {}
                    pack_values.update({'sale_order_id': sale_order_id.id})
                    pack_values.update({'sale_order_line_id': line.id})
                    pack_values.update({'product_id': pack_id.product_id.id})
                    pack_values.update({'product_uom': pack_id.product_uom.id})
                    pack_values.update({'product_uom_qty': pack_id.product_uom_qty})
                    pack_values.update({'iface_mandatory': pack_id.iface_mandatory})
                    pack_result = sale_order_pack_obj.create(pack_values)
                for job_id in product_template_id.product_template_job_ids:
                    jobs_values = {}
                    jobs_values.update({'sale_order_id': sale_order_id.id})
                    jobs_values.update({'sale_order_line_id': line.id})
                    jobs_values.update({'product_job_id': job_id.name.id})
                    job_result = sale_order_job_obj.create(jobs_values)


class SaleOrderPack(models.Model):
    _name = 'sale.order.pack'

    sale_order_id = fields.Many2one('sale.order','Order #', readonly=True)
    sale_order_line_id = fields.Many2one('sale.order.line','Order line #', readonly=True)
    product_id = fields.Many2one('product.template', 'Product', required=True)
    product_uom = fields.Many2one('product.uom', 'Uom', required=True)
    product_uom_qty = fields.Float('Qty', default=1)
    iface_mandatory = fields.Boolean('Mandatory', default=False)
    stock_picking_id = fields.Many2one('stock.picking', 'Picking', readonly=True)
    stock_move_id = fields.Many2one('stock.move', 'Move', readonly=True)


class SaleOrderJob(models.Model):
    _name = 'sale.order.job'
    _rec_name = 'product_job_id'

    def _random_with_N_digits(self, number_digit):
        range_start = 10**(number_digit-1)
        range_end = (10**number_digit)-1
        return randint(range_start, range_end)

    @api.one
    def get_number_of_employee(self):
        self.number_of_employee = len(self.job_employee_ids)

    @api.one
    def trans_close(self):
        self.state = 'done'
        for job_employee_id in self.job_employee_ids:
            job_employee_id.state = 'done'

    sale_order_id = fields.Many2one('sale.order','Order #', readonly=True)
    sale_order_line_id = fields.Many2one('sale.order.line','Order line #', readonly=True)
    product_job_id = fields.Many2one('product.job','Job', readonly=True)
    barcode = fields.Char('Barcode', size=20, readonly=True)
    number_of_employee = fields.Integer("Number of Employee", compute="get_number_of_employee", readonly=True)
    date_start = fields.Datetime('Start Date', readonly=True)
    date_end = fields.Datetime('End Date', readonly=True)
    job_employee_ids = fields.One2many('sale.order.job.employee','sale_order_job_id','Employees')
    state = fields.Selection([('draft','New'), ('open','Open'), ('done','Finish')], "Status", default='open', readonly=True)

    @api.model
    def create(self, vals):
        vals.update({'barcode': self._random_with_N_digits(10)})
        return super(SaleOrderJob, self).create(vals)


class SaleOrderJobEmloyee(models.Model):
    _name = 'sale.order.job.employee'

    sale_order_job_id = fields.Many2one('sale.order.job', 'Job #')
    date_order = fields.Datetime('Date Order', related='sale_order_job_id.sale_order_id.date_order', readonly=True)
    employee_id = fields.Many2one('hr.employee', readonly=True)
    commission_fee_amount = fields.Float("Commission Fee", default=0.0 ,readonly=True)
    state = fields.Selection([('inprogress','In Progress'),('done','Finish'),('claim','Claimed'),('paid','Paid')],'Status', readonly=True, default='inprogress')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        result = {'domain': domain}

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False
                return result

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        if self.employee_id:
            product_tmpl_id = self.product_id.product_tmpl_id
            args = [('product_template_id','=', product_tmpl_id.id),('employee_id','=',self.employee_id.id),('company_id','=', self.env.user.company_id.id)]
            product_template_employee_ids = self.env['product.template.employee'].search(args)
            if len(product_template_employee_ids) == 0 :
                raise Warning('Pricing for Employee not Found')
            else:
                vals['price_unit'] = product_template_employee_ids[0].list_price
        self.update(vals)
        return result

    @api.multi
    @api.onchange('employee_id')
    def employee_id_change(self):
        return self.product_id_change()

    employee_id = fields.Many2one('hr.employee', 'Employee')