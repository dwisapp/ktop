from odoo import models, fields, api, _

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    vehicle_service_id = fields.Many2one('fleet.vehicle.log.services',string='Vehicle Service')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    vehicle_service_part_id = fields.Many2one('fleet.vehicle.log.services.part', string='Vehicle Service Part')


    def _prepare_account_move_line(self, move=False):
        vals = super(PurchaseOrderLine, self)._prepare_account_move_line(move)
        vals['vehicle_id'] = self.vehicle_id.id
        return vals
    
    @api.depends('vehicle_service_id')
    def _compute_qty_received_method(self):
        super(PurchaseOrderLine, self)._compute_qty_received_method()
        for line in self.filtered(lambda l: l.vehicle_service_id):
            line.qty_received_method = 'manual'
            