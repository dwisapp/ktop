from odoo import fields, models, api, SUPERUSER_ID, _
from datetime import timedelta, datetime

class OtpVerification(models.Model):
    _name = "otp.verification"
    _description = 'Otp Verification'

    otp = fields.Text(string="OTP")
    state = fields.Selection([
            ('verified', 'Verified'),
            ('unverified', 'Unverified'),
            ('rejected', 'Rejected')], string="State", default="unverified")
    phone = fields.Char(string="phone")
    user_id = fields.Many2one('res.users', string="User")
    send_time = fields.Datetime()
    otp_type = fields.Selection([('login', "Login"), ('register','Register')])
    create_date_str = fields.Char(string="Create Date", compute="_compute_create_date_str")
    copy_code_url = fields.Char(string="Copy Code URL", compute="_compute_copy_code_url")

    @api.depends('otp')
    def _compute_copy_code_url(self):
        for rec in self:
            if rec.otp:
                rec.copy_code_url = f"https://www.whatsapp.com/otp/code/?otp_type=COPY_CODE&code=otp{rec.otp}"
            else:
                rec.copy_code_url = ""

    @api.depends('create_date')
    def _compute_create_date_str(self):
        for rec in self:
            if rec.create_date:
                rec.create_date_str = (rec.create_date + timedelta(hours=7)).strftime("%d-%b-%Y %H:%M:%S")



    @api.model
    def _cron_delete_verified_otp(self):
        time_to_delete = datetime.now() - timedelta(minutes=10)
        otp = self.search([('send_time', '<=', time_to_delete)])
        otp.write({'state': 'rejected'})


    @api.model
    def create(self,vals):
        vals['send_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        res = super(OtpVerification, self).create(vals)
        res.send_whatsapp()
        return res
    
    @api.model
    def create_otp(self, phone_number, type):
        return "success"


    def send_whatsapp(self):
        self = self.with_user(SUPERUSER_ID)
        user_tz = self.user_id.tz or 'Asia/Jakarta'
        context = self._context
        new_context = dict(context)
        new_context.update({
            'active_model' : 'otp.verification',
            'active_id' : self.id,
            'default_phone' : self.phone,
            'tz' : user_tz,
        })
        whatsapp_composer = self.env['whatsapp.composer'].sudo().with_context(new_context).create({
            'phone': self.phone,
            'res_model': 'otp.verification',
            'res_ids': str(self.ids),
        })
        whatsapp_composer.sudo()._send_whatsapp_template()


