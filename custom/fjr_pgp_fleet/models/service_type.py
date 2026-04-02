from odoo import models, fields, api, _


class ServiceType(models.Model):
    _inherit = 'fleet.service.type'

    product_id = fields.Many2one('product.product', string='Product')


    @api.model
    def create(self, vals):
        service_type = super(ServiceType, self).create(vals)
        product = self.env['product.product'].create({
            'name': service_type.name,
            'type': 'service',
        })
        service_type.write({'product_id': product.id})
        return service_type

    def write(self, vals):
        if 'name' in vals:
            self.product_id.write({'name': vals['name']})
        return super(ServiceType, self).write(vals)
    
    def unlink(self):
        for service_type in self:
            service_type.product_id.unlink()
        return super(ServiceType, self).unlink()