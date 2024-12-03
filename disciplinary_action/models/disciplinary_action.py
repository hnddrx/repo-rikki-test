import random
import string
from odoo import fields, models, api
from datetime import date
import logging

_logger = logging.getLogger(__name__)

class DisciplinaryAction(models.Model):
    _name = "disciplinary.action"
    _description = "Disciplinary Action"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'doc_name'
    
    
    doc_name = fields.Char(string="Name", readonly=True, default='New')
    
    # Many2one relationship field
    incident_report = fields.Many2one('incident.report', string='Incident Report',required=True)
    """  incident_report_description = fields.Text(string='Description', readonly=True) """
    
    sanction = fields.Many2one('sanction.lists', string='Sanction',required=True)
    description = fields.Char(string='Sanction Description', readonly=True, compute='_get_sanction', store=True)
    underwent = fields.Boolean(string='Underwent to a conference', default=False)
    
    terminated_on = fields.Date(string='Terminated On')

    employee = fields.Many2one('hr.employee',string='Employee', required=True)
    employee_name = fields.Char(string='Employee Name', readonly=True, compute='_compute_employee_name', store=True)
    number_of_days = fields.Integer(string='Number of Suspension Days')
    posting_date = fields.Date(string='Posting Date', default=fields.Date.context_today, readonly=True)
    suspended_from = fields.Date(string='Suspended From')
    suspended_to = fields.Date(string='Suspended To')
    admin_hearing_schedule = fields.Date(string="Admin hearing schedule", tracking=True, help="Scheduled date of admin hearing.")
    deduction_amount = fields.Float(string='Deduction Amount')
    
    #Text fields
    hearing_remarks = fields.Text(string='Hearing Remarks')
    remarks = fields.Text(string='Remarks')
    
    @api.model
    def create(self, vals):
        """Generate document name sequence during creation."""
        if vals.get('doc_name', 'New') == 'New':
            vals['doc_name'] = self.env['ir.sequence'].next_by_code('disciplinary.action') or 'New'
        return super(DisciplinaryAction, self).create(vals)

    """   @api.depends('incident_report')
    def _compute_offense(self):
        for record in self:
            record.incident_report_description = record.offense.description if record.offense else ''
            
            """ 
    @api.depends('employee')
    def _compute_employee_name(self):
        for record in self:
            record.employee_name = record.employee.s_full_name if record.employee else ''
            
    @api.depends('sanction')
    def _get_sanction(self):
        for record in self:
            record.description = record.sanction.description if record.sanction else ''
    