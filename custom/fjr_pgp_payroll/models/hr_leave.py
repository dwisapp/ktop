from odoo import models, fields, api, _

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    def _get_duration(self, check_leave_type=True, resource_calendar=None):
        if self.holiday_status_id.time_type == 'other':
            days = (self.date_to - self.date_from).days
            hours = (self.date_to - self.date_from).total_seconds() / 3600
            if days == 0:
                days = 1
            return (days, hours)
        return super(HrLeave, self)._get_duration(check_leave_type=check_leave_type, resource_calendar=resource_calendar)
            