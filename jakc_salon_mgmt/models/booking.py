from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, Warning


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    website_description = fields.Char('Website Description',)


class Appointment(models.Model):
    _name = 'appointment'

    partner_id = fields.Many2one('res.partner','Customer', required=True)
    date_appointment = fields.Date('Appointment Date', required=True)
    company_id = fields.Many2one('res.company','Company', required=True)
    employee_id = fields.Many2one('hr.employee','Employee', required=True)


class AppointmentTimeSlot(models.Model):
    _name = 'appointment.time.slot'

    name = fields.Char()
    time_start = fields.Float('Time Start')
    time_end = fields.Float('Time End')