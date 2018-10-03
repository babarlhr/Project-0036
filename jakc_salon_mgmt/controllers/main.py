# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from datetime import datetime
import json
import werkzeug
import logging

_logger = logging.getLogger(__name__)


class SalonJob(http.Controller):

    @http.route('/salon/job/screen/', type='http', auth='user')
    def salon_job_screen(self, **kwargs):
        # if user not logged in, log him in
        queue_trans_obj = http.request.env['queue.trans']
        pickup_log = http.request.env['queue.pickup.log'].search([
            ('state', '=', 'opened'),
            ('user_id', '=', http.request.session.uid), ], limit=1)
        if pickup_log:
            _logger.info(pickup_log)
            pickup_data = {}
            pickup_data.update({'pickup_id': pickup_log.pickup_id.id})
            return request.render('jakc_queue.pickupscreen', {'pickup': pickup_data})

    @http.route('/salon/job/process/<string:employee_barcode>/<string:job_barcode>/',type='http', auth='user')
    def salon_job_process(self, employee_barcode, job_barcode,  **kwargs):
        sale_order_job_obj = http.request.env['sale.order.job']
        sale_order_job_employee_obj = http.request.env['sale.order.job.employee']
        hr_employee_obj = http.request.env['hr.employee']
        args = [('barcode','=', job_barcode)]
        sale_order_job_id = sale_order_job_obj.search(args, limit=1)
        if sale_order_job_id:
            employee_args = [('barcode','=', employee_barcode)]
            hr_employee_id = hr_employee_obj.search(employee_args, limit=1)
            if hr_employee_id:
                job_employee_vals = {}
                job_employee_vals.update({'sale_order_job_id':sale_order_job_id.id})
                job_employee_vals.update({'employee_id': hr_employee_id.id})
                result = sale_order_job_employee_obj.create(job_employee_vals)
                if result:
                    return '{"success":true,"message":"Employee Registered Successfully"}'
                else:
                    return '{"success":false,"message":"Employee Register Failed"}'

            else:
                return '{"success":false,"message":"Employee not Found"}'
        else:
            return '{"success":false,"message":"Job not Found"}'

