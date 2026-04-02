from odoo import models, fields, api, _
from odoo.addons.account_fleet.models.account_move import AccountMove as AccountMoveFleet


def _post(self, soft=True):
        vendor_bill_service = self.env.ref('account_fleet.data_fleet_service_type_vendor_bill', raise_if_not_found=False)
        if not vendor_bill_service:
            return super(AccountMoveFleet, self)._post(soft)

        val_list = []
        log_list = []
        not_posted_before = self.filtered(lambda r: not r.posted_before)
        posted = super(AccountMoveFleet, self)._post(soft)  # We need the move name to be set, but we also need to know which move are posted for the first time.
        # for line in (not_posted_before & posted).line_ids.filtered(lambda ml: ml.vehicle_id and ml.move_id.move_type == 'in_invoice'):
        #     val = line._prepare_fleet_log_service()
        #     log = _('Service Vendor Bill: %s', line.move_id._get_html_link())
        #     val_list.append(val)
        #     log_list.append(log)
        # log_service_ids = self.env['fleet.vehicle.log.services'].create(val_list)
        # for log_service_id, log in zip(log_service_ids, log_list):
        #     log_service_id.message_post(body=log)
        return posted


AccountMoveFleet._post = _post