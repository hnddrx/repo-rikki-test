from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date
import logging

_logger = logging.getLogger(__name__)

class MedicalType (models.Model):
    _name = 'medical.type'
    _description = 'Medical Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Medical Type', required=True)
    description = fields.Char(string='Description')