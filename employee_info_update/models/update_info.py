from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)


class UpdateInfo(models.Model):
    _name = "update.info"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Employee Info Update"
    _rec_name = 'name'
   
    employee_id = fields.Many2one('hr.employee', string='Employee Name', index=True, ondelete="restrict", tracking=True, required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    department_id = fields.Many2one('hr.department', string='Department')
    update_date = fields.Date(string='Update Date')
    update_detail = fields.One2many('detail.update', inverse_name='update_id', string='Update Detail', required=True)
    
    reason = fields.Text(string='Reason', required=True)
    name = fields.Char(string='Name')

    # workflow setup

    status = fields.Selection([
        ('draft', 'Draft'),
        ('to_submit', 'Submit'),
        ('submitted', 'To Approve'),
        ('reject', 'Rejected'),
        ('approved', 'Approved')
    ], string="Status", default="draft", required=True, readonly=True, tracking=True)

    @api.model
    def default_get(self, fields):
        res = super(UpdateInfo, self).default_get(fields)
        return res
    
    @api.model
    def write(self, vals):
      
        return super(UpdateInfo, self).write(vals)
    
    
    @api.model
    def create(self, vals):
        record = super(UpdateInfo, self).create(vals)
        _logger.info('This is a comment log')
        record.name = f'UI {record.id}'
        return record
        
    
    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            self.company_id = self.employee_id.company_id
            self.department_id = self.employee_id.department_id
            
    #Update employee table data when triggered
    def action_confirm(self):
        vals = {'status': 'approved'}
        employee_vals = {}
        for detail in self.update_detail:
            employee_vals.update({detail.field_id.name: detail.new_value})
        self.write(vals)
        self.employee_id.write(employee_vals)
        2

class DetailUpdate(models.Model):
    _name = "detail.update"
    _description = "Detail Update"
    
    field_name = fields.Char(string='Field Name')
    field_id = fields.Many2one('ir.model.fields', string='Field ID', domain="[('model_id.model', '=', 'hr.employee')]")
    old_value = fields.Char(string='Old Value')
    new_value = fields.Char(string='New Value')
    update_id = fields.Many2one('update.info', string='Update ID')
    
    @api.onchange('field_id')
    def onchange_field_name(self):
        if self.field_id:
            self.old_value = getattr(self.update_id.employee_id, self.field_id.name)
            