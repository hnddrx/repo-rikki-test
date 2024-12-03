from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date
import logging

_logger = logging.getLogger(__name__)

class CertificateOfEmployment(models.Model):
    _name = 'certificate.of.employment'
    _description = 'Certificate of Employment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'doc_name'  # Use the doc_name field as the display name
    
    TYPE_SELECTION = [
        ('coe_with_compensation_monthly', 'COE with Compensation (Monthly)'),
        ('coe_with_compensation_annual', 'COE with Compensation (Annual)'),
        ('coe_without_compensation', 'COE without Compensation'),
    ]
    
    # Fields
    doc_name = fields.Char(string='Document Name', readonly=True, default='New', copy=False)
    employee = fields.Many2one('hr.employee', string='Employee', required=True, tracking=True)
    employee_name = fields.Char(string='Employee Name', readonly=True, compute='_compute_employee_info', store=True)
    first_name = fields.Char(string=_('First Name'), readonly=True, compute='_compute_employee_info', store=True)
    middle_name = fields.Char(string=_('Middle Name'), readonly=True, compute='_compute_employee_info', store=True)
    last_name = fields.Char(string=_('Last Name'), readonly=True, compute='_compute_employee_info', store=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, store=True)
    company = fields.Char(string='Company', readonly=True, compute='_compute_employee_info', store=True)
    department = fields.Char(string='Department', readonly=True, compute='_compute_employee_info', store=True)
    certified_by = fields.Many2one('hr.employee', string='Certified By', compute='_compute_certified_by', store=True)

    # Selection fields
    purpose = fields.Selection([
        ('visa_application', 'Visa Application'),
        ('bank_loan', 'Bank Loan'),
        ('car_loan', 'Car Loan'),
        ('travel', 'Travel'),
        ('school_requirement', 'School Requirements'),
        ('employment_verification', 'Employment Verification'),
        ('credit_card', 'Credit Card'),
        ('legal_purpose', 'Legal Purpose'),
        ('sss_non_cash_advancement', 'SSS Non-Cash Advancement'),
        ('Others', 'Others')
    ], string="Purpose", default='travel', tracking=True)

    others = fields.Text(string="Others", tracking=True)
    from_date = fields.Date(string='From Date', readonly=True, compute='_compute_employee_info', store=True)
    to_date = fields.Date(string='To Date', readonly=True, compute='_compute_employee_info', store=True)
    date_of_travel = fields.Date(string='Date of Travel')
    type = fields.Selection(TYPE_SELECTION, string="Type", tracking=True)


    # Date fields
    posting_date = fields.Date(string='Posting Date', default=fields.Date.context_today, readonly=True)

    # Workflow
    current_docstatus = fields.Integer(string="Current Docstatus", default=0)
    current_sequence = fields.Integer(string="Current Sequence", default=0)
    status = fields.Char(string="Status", tracking=True)
    can_approve = fields.Boolean(string="Can Approve", compute="_compute_can_approve_and_reject")
    # can reject - tagging if the approver has a reject button or not 
    can_reject = fields.Boolean(string="Can Reject", compute="_compute_can_approve_and_reject", store=True)
    can_cancel = fields.Boolean(string="Can Cancel", compute="_compute_can_approve_and_reject", store=True)

    work_flow = fields.Many2one('workflow', string='Workflow', compute='_get_workflow', store=True)

    module_approval_flow = fields.One2many(
        'module.approval.flow',
        'certificate_id',
        string='Module Approval Flow'
    )

    @api.model
    def open_record(self):
        """Method to explicitly trigger the can_approve calculation on record open"""
        self._compute_can_approve_and_reject()
        
    @api.model
    def _compute_can_approve_and_reject(self):
        """Compute permissions to approve, reject, or cancel based on the current user's role in the approval flow."""
        current_user_id = self.env.user.id  # Fetch the current user ID once for efficiency
        """ Use for record in self: to ensure the method works for multiple records and avoids unexpected single-record assumptions. """
        for record in self:
            # Default all permissions to False
            record.can_approve = record.can_reject = record.can_cancel = False

            # Filter relevant approvers for the current user and sequence
            relevant_approvers = record.module_approval_flow.filtered(
                lambda approver: approver.module_approver_name.id == current_user_id and
                                 approver.module_approval_sequence == record.current_sequence
            )

            # Evaluate document status for relevant approvers
            for approver in relevant_approvers:
                if approver.module_doc_status in (1, 2):
                    record.can_approve = True
                elif approver.module_doc_status == 3:
                    record.can_reject = True
                elif approver.module_doc_status == 4:
                    record.can_cancel = True
                """  break  # Exit loop after the first match """
            
            
    """ Action flow """
    def action_submit(self):
        for record in self: 
            record.current_sequence = 0
            record.current_docstatus = 0
            if record.status == 'Draft':
                record.status = 'Pending'
                record.current_sequence += 1 
                record.current_docstatus += 1
                
    def action_approve(self):
        for record in self:
            # Find the first matching approver status (if any)
            approver_status = record.module_approval_flow.filtered(
                lambda a: a.module_approver_name.id == self.env.user.id and a.module_doc_status in (1, 2)
            )
           
            # If a matching approver is found, update the status and sequence
            if approver_status:
                    approver_status = approver_status[0]  # Get the first (and presumably only) matching approver
                    record.status = approver_status.module_approval_status
                    record.current_docstatus = approver_status.module_doc_status
                    approver_status.module_approval_date = fields.Datetime.now()
                    approver_status.module_approval_confirmed = True
                    record.current_sequence += 1      
            
    def action_reject(self):
        for record in self:
            approver_status = record.module_approval_flow.filtered(
                        lambda a: a.module_approver_name.id == self.env.user.id and a.module_doc_status == 3
                    )
        
            if approver_status:
                    approver_status = approver_status[0]  # Get the first (and presumably only) matching approver
                    record.status = approver_status.module_approval_status
                    record.current_docstatus = approver_status.module_doc_status
                    approver_status.module_approval_date = fields.Datetime.now()
                    approver_status.module_approval_confirmed = True
                    
    def action_cancel(self):
        for record in self:
            approver_status = record.module_approval_flow.filtered(
                        lambda a: a.module_approver_name.id == self.env.user.id and a.module_doc_status == 4
                    )
        
            if approver_status:
                    approver_status = approver_status[0]  # Get the first (and presumably only) matching approver
                    record.status = approver_status.module_approval_status
                    record.current_docstatus = approver_status.module_doc_status
                    approver_status.module_approval_date = fields.Datetime.now()
                    approver_status.module_approval_confirmed = True

    @api.depends('work_flow')
    def _populate_approval_flow(self):
        """Populate or append approval flow records for this certificate."""
        for record in self:
            if record.work_flow and record.work_flow.approvals_table:
                approval_values = [
                    {
                        'certificate_id': record.id,
                        'module_approver_name': approval.approver_email.id,
                        'module_approver_email': approval.approver_email.login,
                        'module_approval_status': approval.sequence_status.status_name,
                        'module_doc_status': approval.doc_status,
                        'module_approval_sequence': approval.sequence
                    }
                    for approval in record.work_flow.approvals_table
                ]

                # Bulk create missing approvals
                existing_approval_ids = self.env['module.approval.flow'].search([
                    ('certificate_id', '=', record.id),
                    ('module_approval_sequence', 'in', [approval['module_approval_sequence'] for approval in approval_values])
                ]).ids

                # Create new approvals for missing records
                missing_approvals = [approval for approval in approval_values if approval['module_approval_sequence'] not in existing_approval_ids]
                if missing_approvals:
                    self.env['module.approval.flow'].create(missing_approvals)
                    _logger.info(f"Approval flow appended for certificate {record.id}")
                
                if not approval_values:
                    _logger.warning(f"No approval found for certificate {record.id}")
            else:
                _logger.warning(f"No approval table found for certificate {record.id}")

    @api.depends('employee')
    def _get_workflow(self):
        """Compute and assign the appropriate workflow based on the employee's company."""
        for record in self:
            if not record.employee:
                record.work_flow = False
                continue

            employee_data = record.employee.read(['company_id'])[0]
            company_id = employee_data.get('company_id', [False])[0]
            
            # Search for an active workflow matching the company and module selection
            workflow = self.env['workflow'].search(
                [('company', '=', company_id), ('is_active', '=', True), ('module_selection', '=', 'certificate_of_employment')],
                limit=1
            )
            
            record.work_flow = workflow.id if workflow else False

    @api.model
    def create(self, vals):
        try:
            if vals.get('doc_name', 'New') == 'New':
                vals['doc_name'] = self.env['ir.sequence'].next_by_code('certificate.of.employment') or '/'
            
            vals['status'] = 'Draft'  # Set status to Draft by default
            certificate = super(CertificateOfEmployment, self).create(vals)
            
            if certificate.work_flow:
                certificate._populate_approval_flow()
            return certificate
        except Exception as e:
            _logger.error("Error creating certificate of employment: %s", e)
            raise

    def write(self, vals):
        """Override write to trigger approval flow population when work_flow is updated."""
        res = super(CertificateOfEmployment, self).write(vals)
        if 'work_flow' in vals:
            self._populate_approval_flow()
        return res

    @api.depends('type')
    def _compute_certified_by(self):
        for record in self:
            if record.type:
                signatory = self.env['coe.signatories'].search([('certificate_type', '=', record.type)], limit=1)
                record.certified_by = signatory.signee if signatory else False
            else:
                record.certified_by = False

    @api.depends('employee')
    def _compute_employee_info(self):
        for record in self:
            employee = record.employee
            record.update({
                'employee_name': getattr(employee, 's_full_name', ''),
                'department': getattr(employee.department_id, 'name', ''),
                'first_name': getattr(employee, 's_first_name', ''),
                'middle_name': getattr(employee, 's_middle_name', ''),
                'last_name': getattr(employee, 's_last_name', ''),
                'company': getattr(employee.company_id, 'name', ''),
                'from_date': getattr(employee, 's_date_hired', ''),
                'to_date': getattr(employee, 's_date_of_separation', fields.Date.context_today(record)),
            })

""" Certificate of employment module approval flow """
class ModuleApprovalFlow(models.Model):
    _name = 'module.approval.flow'
    _description = 'Module Approval Flow'

    certificate_id = fields.Many2one(
        'certificate.of.employment',
        string='Certificate of Employment',
        required=True,
        ondelete='cascade'
    )
    module_approver_name = fields.Many2one('res.users', string='Approver Name', store=True)
    module_approver_email = fields.Char(string='Approver Email', store=True)
    module_approval_status = fields.Char(string='Approval Status', store=True)
    module_approval_sequence = fields.Integer(string='Approval Sequence', store=True)
    module_doc_status = fields.Integer(string="Docstatus", store=True)
    module_approval_date =  fields.Datetime(string="Approved On")
    module_approval_confirmed = fields.Boolean(string='Confirmed Approval', store=True)
    
class CoeSignatories(models.Model):
    _name = 'coe.signatories'
    _description = 'Certificate of Employment Signatories'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    certificate_type = fields.Selection(
        selection=lambda self: self.env['certificate.of.employment'].get_type_selection(),
        string='Certificate Type',
        required=True,
        tracking=True
    )
    signee = fields.Many2one('hr.employee', string='Signee', required=True, tracking=True)

