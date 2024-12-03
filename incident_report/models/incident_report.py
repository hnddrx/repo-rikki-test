import random
import string
from odoo import fields, models, api

class IncidentReport(models.Model):
    _name = "incident.report"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Incident Report"
    _rec_name = "doc_name"
    
    #ID
    doc_name = fields.Char(string='Document Name', required=True, readonly=True, default='New')

    # Many2one relationship field
    offense = fields.Many2one('offense.lists', string='Offense',required=True)
    offense_name = fields.Text(string="Offense Name", readonly=True, compute='_compute_offense', store=True)
    offense_description = fields.Text(string="Offense Description", readonly=True, compute='_compute_offense', store=True)
    #char fields
    incident_location = fields.Char(string='Incident Location')
    violation_details = fields.Char(string='Violation Details')
    date_and_time_of_offense = fields.Datetime(string='Date and Time of Offense')
    details_of_violation = fields.Text(string='Details of Violation')
    posting_date = fields.Date(string='Posting Date',required=True,default=lambda self: fields.Datetime.now(),readonly=True)
    damage_done = fields.Text(string='Damage Done')
    attachment_ids = fields.Many2many(
        'ir.attachment', 
        string="Attachments", 
        help="Attachments related to this document"
    )

    
    offense = fields.Many2one('offense.lists', string='Offense')
    offense_description = fields.Char(string='Offense Description', readonly=True, compute='_get_offense', store=True)
    
    
    involved_employees = fields.One2many(
        'involved.employees',
        'incident_report_id',
        string='Employee'
    )
    
    @api.depends('offense')
    def _compute_offense(self):
        for record in self:
            record.offense_description = record.offense.description if record.offense else ''
            record.offense_name = record.offense.offense_name if record.offense else ''

    
    @api.model
    def _generate_random_id(self):
        """Generate a random ID for the incident report."""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    @api.model
    def create(self, vals):
        if vals.get('doc_name', 'New') == 'New':
            vals['doc_name'] = self.env['ir.sequence'].next_by_code('incident.report') or '/'
        return super(IncidentReport, self).create(vals)
    
    @api.depends('offense')
    def _get_offense(self):
        for record in self:
            record.offense_description = record.offense.description if record.offense else ''
            
    
class InvolvedEmployees(models.Model):
    _name = 'involved.employees'
    _description = 'Involved Employees'
    
    incident_report_id = fields.Many2one('incident.report', string="Incident Report")
    employee = fields.Many2one('hr.employee', string="Employee ID", required=True)
    employee_name =  fields.Char(string="Employee Name", readonly=True, compute='_compute_employee_name', store=True)
    involvement  = fields.Selection([('offender', 'Offender'), ('complainant', 'Complainant'), ('witness', 'Witness')],string="Involvement")
    department = fields.Char(string="Department", readonly=True, compute='_compute_employee_name', store=True)
    
    @api.depends('employee')
    def _compute_employee_name(self):
        for record in self:
            record.employee_name = record.employee.name if record.employee else ''
            record.department = record.employee.department_id.name if record.employee else ''