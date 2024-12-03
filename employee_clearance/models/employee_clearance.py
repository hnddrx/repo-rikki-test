from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class EmployeeClearance(models.Model):
    _name = 'employee.clearance'
    _description = 'Employee Clearance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'doc_name'

    # Employee Clearance Name
    doc_name = fields.Char(string="Document Name", readonly=True, default='New', copy=False)

    # Employee Information
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    employee_name = fields.Char(string="Employee Name", readonly=True, compute='_compute_employee_info', store=True)
    position_title = fields.Char(string="Position Title", readonly=True, compute='_compute_employee_info', store=True)
    employment_status = fields.Char(string="Employee Status", readonly=True, compute='_compute_employee_info', store=True)
    company = fields.Char(string="Company", readonly=True, compute='_compute_employee_info', store=True)
    department = fields.Char(string="Department", readonly=True, compute='_compute_employee_info', store=True)

    # Clearance Information
    reason_for_leaving = fields.Text(string="Reason for Leaving")
    company_email = fields.Char(string="Company Email")
    remarks = fields.Text(string="Remarks")
    last_working_date = fields.Date(string="Last Working Date")
    effective_date = fields.Date(string="Effective Date")
    posting_date = fields.Date(string='Posting Date', default=fields.Date.context_today, readonly=True)

    # Clearance Type and Authorizations
    clearance_type = fields.Selection(
        [
            ('Resignation', 'Resignation'),
            ('Retirement', 'Retirement'),
            ('Regularization', 'Regularization'),
            ('Termination', 'Termination'),
        ], 
        string='Clearance Type', 
        required=True
    )
    
    authorize_ids = fields.One2many(
        'department.manager',
        'clearance_id',  # Corrected reverse relation field
        string='Authorized',
        copy=True
    )

    # Signee Information
    conforme_employee_name = fields.Many2one('hr.employee', string='Conforme')
    contact_number = fields.Char(string='Contact Number')
    signed_date = fields.Date(string='Signed Date')  # Date field instead of Char

    @api.model
    def create(self, vals):
        """Generate document name sequence during creation."""
        if vals.get('doc_name', 'New') == 'New':
            vals['doc_name'] = self.env['ir.sequence'].next_by_code('employee.clearance') or 'New'
        return super(EmployeeClearance, self).create(vals)

    def action_save(self):
        """Custom save action."""
        self.ensure_one()
        _logger.info(f"Saving Employee Clearance {self.doc_name}")

    @api.depends('employee_id')
    def _compute_employee_info(self):
        """Compute employee-related fields."""
        for record in self:
            employee = record.employee_id
            if employee:
                record.employee_name = employee.s_full_name
                record.department = employee.department_id.name
                record.company = employee.company_id.name
                record.company_email = employee.company_id.email
                record.position_title = employee.job_title
               
            else:
                record.employee_name = ''
                record.department = ''
                record.company = ''
                record.company_email = ''
                record.position_title = ''

class DepartmentManager(models.Model):
    _name = 'department.manager'
    _description = 'Department Manager Clearance'

    # Link back to the clearance record
    clearance_id = fields.Many2one('employee.clearance', string="Clearance", required=True, ondelete='cascade')

    # Clearance Details
    authorized = fields.Many2one('hr.employee', string='Authorized', required=True)
    accountability = fields.Char(string="Accountability")
    status = fields.Selection(
        [('cleared', 'Cleared'), ('not-cleared', 'Not Cleared')], 
        string="Status"
    )
    remarks = fields.Text(string='Remarks')
    date = fields.Date(string="Date")
