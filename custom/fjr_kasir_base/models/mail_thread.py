from odoo import models, fields, api, _


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'


    message_attachment_ids = fields.Many2many('ir.attachment', compute="_compute_message_attachment_ids")


    def _compute_message_attachment_ids(self):
        read_group_var = self.env['ir.attachment']._read_group([('res_id', 'in', self.ids), ('res_model', '=', self._name)],
                                                              groupby=['res_id'],
                                                              aggregates=['id:recordset'],
                                                              )
        attachment_count_dict = dict(read_group_var)

        for record in self:
            record.message_attachment_ids = attachment_count_dict.get(record.id, [])


        