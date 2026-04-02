from odoo import models, fields, api, _


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'


    jatuh_tempo_pajak_tahunan = fields.Date(string='Jatuh Tempo Pajak Tahunan')
    jatuh_tempo_pajak_5_tahunan = fields.Date(string='Jatuh Tempo Pajak 5 Tahunan')
    no_lambung = fields.Char(string='No Lambung')
    no_kir_kepala = fields.Char(string='No KIR Kepala')
    masa_berlaku_kir_kepala = fields.Date(string='Masa Berlaku KIR Kepala')
    nomer_kir_buntut = fields.Char(string='No KIR Buntut')
    masa_berlaku_kir_buntut = fields.Date(string='Masa Berlaku KIR Buntut')
    fleet_document_ids = fields.One2many('fleet.document', 'fleet_id', string='Fleet Documents')
    fleet_document_count = fields.Integer(compute='_compute_fleet_document_count', string='Fleet Document Count')

    @api.depends('fleet_document_ids')
    def _compute_fleet_document_count(self):
        for record in self:
            record.fleet_document_count = len(record.fleet_document_ids)

    def action_open_fleet_document(self):
        action = self.env['ir.actions.act_window']._for_xml_id('fjr_pgp_fleet.fleet_document_action')
        action['domain'] = [('fleet_id', '=', self.id)]
        action['context'] = {
            'default_fleet_id': self.id,
        }
        return action


    def action_open_fleet_stock_usage(self):
        return {
            'name': _('Fleet Item Usage'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'stock.move',
            'domain': [('fleet_item_usage_id.fleet_id', '=', self.id), ('state', '!=', 'cancel'),
                       ('fleet_item_usage_id.state','!=','cancel')],
            'views': [(self.env.ref('fjr_pgp_fleet.stock_move_view_fleet_usage_tree').id, 'tree')],
        }