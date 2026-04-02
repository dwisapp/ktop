from odoo import models, fields, api, _

class WizardReturnFleetItemUsage(models.TransientModel):
    _name = 'wizard.return.fleet.item.usage'
    _description = "Wizard Return Fleet Item Usage"

    fleet_item_usage_id = fields.Many2one('fleet.item.usage', string='Fleet Item Usage', required=True)
    line_ids = fields.One2many('wizard.return.fleet.item.usage.line', 'wizard_return_fleet_item_usage_id', string='Lines')

    def action_return(self):
        move_vals = []
        for line in self.line_ids.filtered(lambda x: x.quantity_return > 0):
            move_vals.append({
                'product_id': line.product_id.id,
                'name': line.product_id.name,
                'product_uom_qty': line.quantity_return,
                'product_uom': line.product_id.uom_id.id,
                'location_id': self.fleet_item_usage_id.location_dest_id.id,
                'location_dest_id': self.fleet_item_usage_id.location_id.id,
                'fleet_item_return_id': self.fleet_item_usage_id.id,
                'stock_move_usage_id': line.origin_move_id.id,
                'is_inventory': True,
                'picked': True,
                'origin': self.fleet_item_usage_id.name,
                'quantity' : line.quantity_return,
            })

        self.env['stock.move'].sudo().create(move_vals)
        self.fleet_item_usage_id.return_move_ids.with_context(inventory_mode=False)._action_done(cancel_backorder=True)
        self.fleet_item_usage_id.write({'state': 'return'})

class WizardReturnFleetItemUsageLine(models.TransientModel):
    _name = 'wizard.return.fleet.item.usage.line'
    _description = "Wizard Return Fleet Item Usage Line"

    wizard_return_fleet_item_usage_id = fields.Many2one('wizard.return.fleet.item.usage', string='Wizard Return Fleet Item Usage')
    product_id = fields.Many2one('product.product', string='Item')
    origin_move_id = fields.Many2one('stock.move', string='Origin Move')
    quantity_used = fields.Float(string='Quantity Used')
    quantity_return = fields.Float(string='Quantity Return')