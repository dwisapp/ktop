from odoo.http import request
from odoo import http, _, fields
from odoo.exceptions import UserError
from math import ceil

class DeliveryNoteApi(http.Controller):
    
    @http.route('/api/delivery_note', type='json', auth='jwt', methods=['GET'], csrf=False)
    def get_delivery_notes(self):
        """
        Retrieve all delivery notes.
        """
        kwargs = request.httprequest.args
        domain = []
        if kwargs.get('product_id'):
            domain.append(('line_ids.product_id.name', 'ilike', kwargs.get('product_id')))
        
        if kwargs.get('sale_order_id'):
            domain.append(('sale_order_ids.name', 'ilike', kwargs.get('sale_order_id')))

        if kwargs.get('partner_id'):
            domain.append(('partner_id.name', 'ilike', kwargs.get('partner_id')))
        if kwargs.get('name'):
            domain.append(('name', 'ilike', kwargs.get('name')))
        
        order_by = kwargs.get("order", "name desc")
        limit = int(kwargs.get("limit", 1000))
        page = int(kwargs.get("page", 1))
        offset = (page - 1) * limit

        delivery_notes = request.env['delivery.note'].search(domain, order=order_by, limit=limit, offset=offset)
        total_delivery_notes = request.env['delivery.note'].search_count(domain)
        delivery_notes_data = []
        total_pages = ceil(total_delivery_notes / limit)
        
        for delivery_note in delivery_notes:
            delivery_notes_data.append(self._prepare_delivery_note_data(delivery_note))
        
        return {
            'delivery_notes': delivery_notes_data,
            'total_count': total_delivery_notes,
            'total_pages': total_pages,
            'current_page': page,
            'limit': limit
        }
    
    @http.route('/api/delivery_note/<int:delivery_note_id>', type='json', auth='jwt', methods=['GET'], csrf=False)
    def get_delivery_note(self, delivery_note_id):
        """
        Retrieve a specific delivery note by its ID.
        """
        delivery_note = request.env['delivery.note'].sudo().search([('id', '=', delivery_note_id)])
        if not delivery_note:
            raise UserError(_("Delivery note with ID %s does not exist.") % delivery_note_id)
        
        return self._prepare_delivery_note_data_detail(delivery_note)
    

    @http.route('/api/delivery_note/<int:delivery_note_id>', type='json', auth='jwt', methods=['PUT'], csrf=False)
    def update_delivery_note(self, delivery_note_id, **kwargs):
        """
        Update a specific delivery note by its ID.
        """
        delivery_note = request.env['delivery.note'].sudo().search([('id', '=', delivery_note_id)])
        if not delivery_note:
            raise UserError(_("Delivery note with ID %s does not exist.") % delivery_note_id)
        
        # Update fields based on kwargs
        

        write_vals = {}
        available_fields = self._get_available_write_fields()
        available_fields_line = self._get_available_write_line_fields()
        for field, value in kwargs.items():
            if field in available_fields:
                if field == 'item_ids':
                    # Handle item_ids separately
                    if isinstance(value, list):
                        item_lines = []
                        for item in value:
                            item_line_val = {}
                            if item['type'] == 'create':
                                # Create new line
                                
                                for item_field, item_value in item['value'].items():
                                    

                                    if item_field in available_fields_line:
                                        item_line_val[available_fields_line[item_field]] = item_value
                                item_lines.append((0, 0, item_line_val))

                            elif item['type'] == 'edit':
                                if not item.get('id', False):
                                    raise UserError(_("Item ID is required for editing."))
                                for item_field, item_value in item['value'].items():
                                    if item_field in available_fields_line:
                                        item_line_val[available_fields_line[item_field]] = item_value
                                item_lines.append((1, item['id'], item_line_val))

                            elif item['type'] == 'delete':
                                if not item.get('id', False):
                                    raise UserError(_("Item ID is required for deletion."))
                                item_lines.append((2, item['id']))
                            
                            else:
                                raise UserError(_("Invalid item type. Expected 'create', 'edit', or 'delete'."))
                        write_vals[available_fields[field]] = item_lines
                        
                    else:
                        raise UserError(_("Invalid format for item_ids. Expected a list of items."))

                else:
                    write_vals[available_fields[field]] = value

        if not write_vals:
            raise UserError(_("No valid fields provided for update."))
        
        delivery_note.sudo().write(write_vals)
        
        return self._prepare_delivery_note_data_detail(delivery_note)
    

    def _get_available_write_line_fields(self):
        """
        Returns a list of fields that can be updated for delivery note lines via the API.
        """
        return {
            "product_id": "product_id",
            "quantity": "product_uom_qty",
            "product_uom": "product_uom",
            "price_unit": "price_unit",
            "other_quantity": "other_quantity",
            "other_uom_id": "other_uom_id",
            "no_container": "no_container",
        }


    def _get_available_write_fields(self):
        """
        Returns a list of fields that can be updated via the API.
        """
        return {
            "partner_id" : "partner_id",
            "customer_order_ref" : "customer_order_ref",
            "delivery_start_date" : "delivery_start_date",
            "delivery_finish_date" : "delivery_finish_date",
            "transporter_id" : "transporter_id",
            "driver_id" : "driver_employee_id",
            "transport_receipt_no" : "transport_receipt_no",
            "vehicle_id" : "fleet_id",
            "transport_mode" : "transport_mode",
            "transport_receipt_date" : "transport_receipt_date",
            "distance_km" : "distance",
            "tempat_muat_id" : "tempat_muat_id",
            "detail_tempat_muat" : "tempat_muat",
            "tujuan_bongkar_id" : "tujuan_bongkar_id", 
            "detail_tujuan_bongkar" : "tujuan_bongkar",
            "item_ids" : "line_ids",        
        }


    @http.route('/api/delivery_note/<int:delivery_note_id>', type='json', auth='jwt', methods=['DELETE'], csrf=False)
    def delete_delivery_note(self, delivery_note_id):
        """
        Delete a specific delivery note by its ID.
        """
        delivery_note = request.env['delivery.note'].sudo().search([('id', '=', delivery_note_id)])
        if not delivery_note:
            raise UserError(_("Delivery note with ID %s does not exist.") % delivery_note_id)
        
        delivery_note.sudo().unlink()
        
        return _("Delivery note with ID %s has been deleted.") % delivery_note_id


    def _prepare_delivery_note_data(self, delivery_note):
        state_values = dict(request.env["delivery.note"]._fields['state'].selection)
        return {
            'id': delivery_note.id,
            'name': delivery_note.name,
            'partner_id': {
                'id': delivery_note.partner_id.id,
                'name': delivery_note.partner_id.name,
            },
            'transport_receipt_no' : delivery_note.transport_receipt_no or '',
            'tempat_muat_id': {
                'id': delivery_note.tempat_muat_id.id,
                'name': delivery_note.tempat_muat_id.name,
            } if delivery_note.tempat_muat_id else {},
            'detail_tempat_muat': delivery_note.tempat_muat,
            'tujuan_bongkar_id': {
                'id': delivery_note.tujuan_bongkar_id.id,
                'name': delivery_note.tujuan_bongkar_id.name,
            } if delivery_note.tujuan_bongkar_id else {},
            'detail_tujuan_bongkar': delivery_note.tujuan_bongkar or '',
            'vehicle_id': {
                'id': delivery_note.fleet_id.id,
                'name': delivery_note.fleet_id.display_name,
            } if delivery_note.fleet_id else {},
            'driver_id': {
                'id': delivery_note.driver_employee_id.id,
                'name': delivery_note.driver_employee_id.name,
            } if delivery_note.driver_employee_id else {},
            
            'jenis_barang': delivery_note.jenis_barang or '',
            'tempat_muat': delivery_note.tempat_muat or '',
            'tujuan_bongkar': delivery_note.tujuan_bongkar or '',
            'delivery_start_date': fields.Datetime.to_string(fields.Datetime.context_timestamp(delivery_note, delivery_note.delivery_start_date)) if delivery_note.delivery_start_date else '',
            'delivery_end_date': fields.Datetime.to_string(fields.Datetime.context_timestamp(delivery_note, delivery_note.delivery_finish_date)) if delivery_note.delivery_finish_date else '',
            'status': {
                'id': delivery_note.state,
                'name': state_values.get(delivery_note.state, ''),
            }
        }
    
    def _prepare_delivery_note_data_detail(self, delivery_note):
        delivery_note_data = self._prepare_delivery_note_data(delivery_note)
        transport_mode_values = dict(request.env["delivery.note"]._fields['transport_mode'].selection)
        delivery_note_data['item_ids'] = []
        delivery_note_data.update({
            'transport_mode': {
                'id': delivery_note.transport_mode,
                'name': transport_mode_values.get(delivery_note.transport_mode, ''),
            } if delivery_note.transport_mode else {},
            'transport_receipt_date': fields.Datetime.to_string(fields.Datetime.context_timestamp(delivery_note, delivery_note.transport_receipt_date)) if delivery_note.transport_receipt_date else '',
            'distance_km': delivery_note.distance,
            'employee_id': {
                'id': delivery_note.employee_id.id,
                'name': delivery_note.employee_id.name,
            } if delivery_note.employee_id else {},
            'customer_order_ref': delivery_note.customer_order_ref or '',
            'notes': delivery_note.notes or '',
            })
        
        for line in delivery_note.line_ids:
            delivery_note_data['item_ids'].append({
                'id': line.id,
                'product_id': {
                    'id': line.product_id.id,
                    'name': line.product_id.name,
                },
                'quantity': line.product_uom_qty,
                'product_uom': {
                    'id': line.product_uom.id,
                    'name': line.product_uom.name,
                },
                'price_unit': line.price_unit,
                'other_quantity': line.other_quantity,
                'other_uom_id': {
                    'id': line.other_uom_id.id,
                    'name': line.other_uom_id.name,
                } if line.other_uom_id else {},
                'no_container' : line.no_container or '',
            })
        
        return delivery_note_data
    

    @http.route('/api/drivers', type='json', auth='jwt', methods=['GET'], csrf=False)
    def get_drivers(self):
        """
        Retrieve all drivers.
        """
        domain = [('is_driver', '=', True)]
        kwargs = request.httprequest.args
        if kwargs.get('name'):
            domain.append(('name', 'ilike', kwargs.get('name')))

        drivers = request.env['hr.employee'].search(domain)
        driver_data = []
        
        for driver in drivers:
            driver_data.append({
                'id': driver.id,
                'name': driver.name,
            })
        
        return {
            'drivers': driver_data,
            'total_count': len(driver_data),
        }
    

    @http.route('/api/vehicles', type='json', auth='jwt', methods=['GET'], csrf=False)
    def get_vehicles(self):
        """
        Retrieve all vehicles.
        """
        domain = []
        kwargs = request.httprequest.args
        if kwargs.get('name'):
            domain.append("|", ('name', 'ilike', kwargs.get('name')), ('license_plate', 'ilike', kwargs.get('name')))

        vehicles = request.env['fleet.vehicle'].search(domain)
        vehicle_data = []
        
        for vehicle in vehicles:
            vehicle_data.append({
                'id': vehicle.id,
                'name': vehicle.display_name,
            })
        
        return {
            'vehicles': vehicle_data,
            'total_count': len(vehicle_data),
        }


    @http.route('/api/tempat-muat', type='json', auth='jwt', methods=['GET'], csrf=False)
    def get_tempat_muat(self):
        """
        Retrieve all loading places.
        """
        domain = []
        kwargs = request.httprequest.args
        if kwargs.get('name'):
            domain.append(('name', 'ilike', kwargs.get('name')))
        tempat_muats = request.env['res.tempat.muat'].search(domain)
        tempat_muat_data = []
        
        for tempat_muat in tempat_muats:
            tempat_muat_data.append({
                'id': tempat_muat.id,
                'name': tempat_muat.name,
            })
        
        return {
            'tempat_muats': tempat_muat_data,
            'total_count': len(tempat_muat_data),
        }
    
    @http.route('/api/tujuan-bongkar', type='json', auth='jwt', methods=['GET'], csrf=False)
    def get_tujuan_bongkar(self):
        """
        Retrieve all unloading destinations.
        """

        domain = []
        kwargs = request.httprequest.args
        if kwargs.get('name'):
            domain.append(('name', 'ilike', kwargs.get('name')))
        tujuan_bongkars = request.env['res.tujuan.bongkar'].search(domain)
        tujuan_bongkar_data = []
        
        for tujuan_bongkar in tujuan_bongkars:
            tujuan_bongkar_data.append({
                'id': tujuan_bongkar.id,
                'name': tujuan_bongkar.name,
            })
        
        return {
            'tujuan_bongkars': tujuan_bongkar_data,
            'total_count': len(tujuan_bongkar_data),
        }
    

    @http.route('/api/products', type='json', auth='jwt', methods=['GET'], csrf=False)
    def get_products(self):
        """
        Retrieve all products.
        """
        domain = [('sale_ok', '=', True)]
        kwargs = request.httprequest.args
        if kwargs.get('name'):
            domain.append(('name', 'ilike', kwargs.get('name')))
        if kwargs.get('code'):
            domain.append(('default_code', 'ilike', kwargs.get('code')))


        products = request.env['product.product'].search(domain)
        product_data = []
        
        for product in products:
            product_data.append({
                'id': product.id,
                'name': product.name,
                'code': product.default_code or '',
                'default_uom_id': {
                    'id': product.uom_id.id,
                    'name': product.uom_id.name,
                } if product.uom_id else {},
            })
        
        return {
            'products': product_data,
            'total_count': len(product_data),
        }
    
    @http.route('/api/product-uoms/<int:product_id>', type='json', auth='jwt', methods=['GET'], csrf=False)
    def get_product_uoms(self, product_id):
        """
        Retrieve all UOMs for a specific product.
        """
        product = request.env['product.product'].sudo().search([('id', '=', product_id)])
        if not product:
            raise UserError(_("Product with ID %s does not exist.") % product_id)
        
        uom_data = []
        for uom in product.uom_id.category_id.uom_ids:
            uom_data.append({
                'id': uom.id,
                'name': uom.name,
            })
        
        return {
            'uoms': uom_data,
            'total_count': len(uom_data),
        }


    @http.route('/api/transporters', type='json', auth='jwt', methods=['GET'], csrf=False)
    def get_transporters(self):

        transporters = request.env['res.partner'].search([('is_transporter', '=', True)])
        transporter_data = []
        for transporter in transporters:
            transporter_data.append({
                'id': transporter.id,
                'name': transporter.name,
            })
        return {
            "transporters" : transporter_data,
            "total_count": len(transporter_data),
        }