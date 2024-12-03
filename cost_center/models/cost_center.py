from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)

class CostCenter(models.Model):
    _name = 'cost.center'
    _description = 'Cost Center'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'doc_name'

    doc_name = fields.Char(string='Document Name', readonly=True, default='New', copy=False)
    cost_center_name = fields.Char(string="Cost Center Name", required=True, tracking=True)
    cost_center_code = fields.Char(string="Cost Center Code", required=True, tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('doc_name') == 'New':
            try:
                vals['doc_name'] = self.env['ir.sequence'].next_by_code('cost.center') or '/'
            except Exception as e:
                _logger.error("Error generating document name for Cost Center: %s", e)
                raise UserError(_("Unable to generate document name. Please contact the administrator."))

        return super(CostCenter, self).create(vals)
