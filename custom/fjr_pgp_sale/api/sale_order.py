from odoo.http import request
from odoo import http, _, fields
from odoo.exceptions import UserError
from math import ceil

class SaleOrderApi(http.Controller):
    
    @http.route('/api/sale_order', type='json', auth='jwt', methods=['GET'], csrf=False)
    def get_sale_orders(self):
        """
        Retrieve all sale orders.
        """

        kwargs = request.httprequest.args
        domain = [('state','=','sale')]
        
        if kwargs.get('partner_id'):
            domain.append(('partner_id.name', 'ilike', kwargs.get('partner_id')))
        if kwargs.get('name'):
            domain.append(('name', 'ilike', kwargs.get('name')))
        if kwargs.get('product_id'):
            domain.append(('order_line.product_id.name', 'ilike', kwargs.get('product_id')))
        if kwargs.get('sales_person_id'):
            domain.append(('user_id.name', 'ilike', kwargs.get('salesperson_id')))


        order_by = kwargs.get("order", "name desc")
        limit = int(kwargs.get("limit", 1000))
        page = int(kwargs.get("page", 1))
        offset = (page - 1) * limit

        sale_orders = request.env['sale.order'].search(domain, order=order_by, limit=limit, offset=offset)
        total_sale_orders = request.env['sale.order'].search_count(domain)
        sale_orders_data = []
        total_pages = ceil(total_sale_orders / limit)
        for sale_order in sale_orders:
            sale_orders_data.append(self._prepare_sale_order_data(sale_order))
    
        return {
            'sale_orders': sale_orders_data,
            'total_count': total_sale_orders,
            'total_pages': total_pages,
            'current_page': page,
            'limit': limit
        }
    
    @http.route('/api/sale_order/<int:sale_order_id>', type='json', auth='jwt', methods=['GET'], csrf=False)
    def get_sale_order(self, sale_order_id):
        """
        Retrieve a specific sale order by its ID.
        """
        sale_order = request.env['sale.order'].sudo().search([('id', '=', sale_order_id)])
        if not sale_order:
            raise UserError(_("Sale order with ID %s does not exist.") % sale_order_id)
        

        return self._prepare_sale_order_data_detail(sale_order)

    @http.route('/api/sale_order/<int:sale_order_id>/create-delivery-note', type='json', auth='jwt', methods=['POST'], csrf=False)
    def create_delivery_note_for_sale_order(self, sale_order_id):
        """
        Create a delivery note for a specific sale order.
        """
        sale_order = request.env['sale.order'].sudo().search([('id', '=', sale_order_id)])
        if not sale_order:
            raise UserError(_("Sale order with ID %s does not exist.") % sale_order_id)

        if not sale_order.state == 'sale':
            raise UserError(_("Sale order must be in 'sale' state to create a delivery note."))

        
        delivery_note = request.env['delivery.note'].create(sale_order._prepare_delivery_note_vals())
        return {
            'delivery_note_id': delivery_note.id,
        }


    def _prepare_sale_order_data(self, sale_order):
        """
        Prepare the data for a sale order.
        """
        state_values = dict(request.env["sale.order"]._fields['state'].selection)
        return {
            'id': sale_order.id,
            'name': sale_order.name,
            'partner_id': {
                'id': sale_order.partner_id.id,
                'name': sale_order.partner_id.name,
            },
           
            'date_order': fields.Datetime.context_timestamp(sale_order, sale_order.date_order).strftime('%Y-%m-%d %H:%M:%S'),
            'amount_total': sale_order.amount_total,
            'status': {
                'id': sale_order.state,
                'name': state_values.get(sale_order.state, ''),
            },
            'sales_person_id': {
                'id': sale_order.user_id.id,
                'name': sale_order.user_id.name,
            }
        }
    
    
    def _prepare_sale_order_data_detail(self, sale_order):
        sale_order_data = self._prepare_sale_order_data(sale_order)


        sale_order_data.update({
            'rute_id': {
                'id': sale_order.rute_uang_jalan_id.id,
                'name': sale_order.rute_uang_jalan_id.name,
            } if sale_order.rute_uang_jalan_id else {},
            'jenis_barang': sale_order.jenis_barang,
            'kapal_id': {
                'id': sale_order.kapal_id.id,
                'name': sale_order.kapal_id.name,
            } if sale_order.kapal_id else {},
            'tempat_muat_id': {
                'id': sale_order.tempat_muat_id.id,
                'name': sale_order.tempat_muat_id.name,
            } if sale_order.tempat_muat_id else {},
            'detail_tempat_muat': sale_order.tempat_muat,
            'tujuan_bongkar_id': {
                'id': sale_order.tujuan_bongkar_id.id,
                'name': sale_order.tujuan_bongkar_id.name,
            } if sale_order.tujuan_bongkar_id else {},
            'detail_tujuan_bongkar': sale_order.tujuan_bongkar,
            

            'order_lines': [
                {
                    'id': line.id,
                    'product_id': {
                        'id': line.product_id.id,
                        'name': line.product_id.name,
                    },
                    'product_uom': {
                        'id': line.product_uom.id,
                        'name': line.product_uom.name,
                    },
                    'quantity': line.product_uom_qty,
                    'price_unit': line.price_unit,
                    'price_subtotal': line.price_subtotal,
                    'price_total': line.price_total,
                    'qty_delivered': line.qty_delivered,
                    'qty_invoiced': line.qty_invoiced,
                    
                } for line in sale_order.order_line
            ]
        })

        return sale_order_data
    

    @http.route('/api/customers', type='json', auth='jwt', methods=['GET'], csrf=False)
    def get_customers(self):
        """
        Retrieve all customers.
        """
        customers = request.env['res.partner'].search([('customer_rank', '>', 0)])
        customer_data = []
        
        for customer in customers:
            customer_data.append({
                'id': customer.id,
                'name': customer.name,
            })
        
        return {
            'customers': customer_data,
            'total_count': len(customer_data),
        }