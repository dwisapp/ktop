from odoo import models, fields, api, _

class HrContract(models.Model):
    _inherit = 'hr.contract'

    payroll_structure_id = fields.Many2one('hr.payroll.structure', string='Payroll Structure', domain="[('type_id', '=', structure_type_id)]")

    tunj_fee = fields.Monetary(string='Fee', help="Fee", tracking=True)
    tunj_transport = fields.Monetary(string='Tunjangan Transport', tracking=True)
    tunj_pulsa = fields.Monetary(string='Tunjangan Pulsa', tracking=True)
    tunj_makan = fields.Monetary(string='Tunjangan Makan', tracking=True)
    tunj_operasional = fields.Monetary(string='Tunjangan Operasional', tracking=True)
    tunj_stand_by = fields.Monetary(string='Tunjangan Stand By', tracking=True)
    tunj_shift = fields.Monetary(string='Tunjangan Shift', tracking=True)
    tunj_jabatan = fields.Monetary(string='Tunjangan Jabatan', tracking=True)
    tunj_wakil_direktur = fields.Monetary(string='Tunjangan Wakil Direktur', tracking=True)
    tunj_all_in = fields.Monetary(string='Tunjangan All In', tracking=True)
    tunj_wilayah = fields.Monetary(string='Tunjangan Wilayah', tracking=True)
    tunj_kuliah = fields.Monetary(string='Tunjangan Kuliah', tracking=True)
    tunj_keahlian = fields.Monetary(string='Tunjangan Keahlian', tracking=True)
    tunj_perumahan = fields.Monetary(string='Tunjangan Perumahan', tracking=True)
    tunj_supir = fields.Monetary(string='Tunjangan Supir', tracking=True)
    potongan_amal_jariyah = fields.Monetary(string="Potongan Amal Jariyah", tracking=True)

    bpjs_active = fields.Boolean(string='BPJS',
                                 help="Check this box if this employee has BPJS active",
                                 tracking=True, default=True)
    bpjs_type = fields.Selection([
        ('full', 'Full Pribadi(5%)'),
        ('perusahaan', 'Perusahaan (4%) + Pribadi (1%)'),
    ], string='BPJS Type', tracking=True, default='perusahaan')
    additional_bpjs = fields.Boolean(string='Additional BPJS (1%)', 
                                        help="Check this box if this employee has additional BPJS (1%)",
                                        tracking=True)  

    jkm_active = fields.Boolean(string='JKM',
                                help="Check this box if this employee has JKM active",
                                tracking=True, default=True)
    jht_active = fields.Boolean(string='JHT',
                                help="Check this box if this employee has JHT active", tracking=True, default=True)
    jp_active = fields.Boolean(string='JP',
                               help="Check this box if this employee has JP active",
                               tracking=True, default=True)
    jkk_active = fields.Boolean(string='JKK',
                                help="Check this box if this employee has JKK active",
                                tracking=True, default=True)
    
    subsidi_driver = fields.Boolean(string='Subsidi Driver', tracking=True)
    nominal_subsidi_driver = fields.Monetary(string='Nominal Subsidi Driver', tracking=True)

    def _get_sub_leave_domain(self):
        include_working_type = self._context.get('include_working_type', False)
        if not include_working_type:
            return super(HrContract, self)._get_sub_leave_domain() + [('time_type', '!=', 'other')]
        return super(HrContract, self)._get_sub_leave_domain()