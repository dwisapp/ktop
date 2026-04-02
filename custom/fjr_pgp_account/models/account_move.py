from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    pic_user_id = fields.Many2one('res.users', string='PIC Signature', domain=lambda self: [('groups_id', 'in', self.env.ref('account.group_account_manager').id)], 
                                  default=lambda self: self.env['res.users'].search([('groups_id', 'in', self.env.ref('account.group_account_manager').id)], limit=1),)
    
    kapal_id = fields.Many2one('kapal.kapal', string='Kapal')
    tanggal_mulai_kegiatan = fields.Date(string='Tanggal Mulai Kegiatan', default=fields.Date.context_today)
    tanggal_selesai_kegiatan = fields.Date(string='Tanggal Selesai Kegiatan', default=fields.Date.context_today)
    term_condition_id = fields.Many2one('account.term.condition', string='Term & Condition')
    invoice_number_custom = fields.Char(string='Invoice Number Custom', )
    use_specific_invoice_sequence = fields.Boolean(string='Use Specific Invoice Sequence', help="If this field is checked, the system will use the specific invoice sequence for this partner", compute='_compute_use_specific_invoice_sequence', store=True)

    @property
    def _sequence_monthly_regex(self):
        return self.journal_id.sequence_monthly_regex or super()._sequence_monthly_regex
    
    @property
    def _sequence_yearly_regex(self):
        return self.journal_id.sequence_yearly_regex or super()._sequence_yearly_regex
    
    @property
    def _sequence_year_range_regex(self):
        return self.journal_id.sequence_year_range_regex or super()._sequence_year_range_regex


    def write(self, vals):
        for move in self:
            if 'name' in vals and move.posted_before and move.use_specific_invoice_sequence:
                vals['invoice_number_custom'] = vals['name']

        return super(AccountMove, self).write(vals)
                


    def _post(self, soft=True):
        for move in self:
            if not move.posted_before or move.name == '/':
                if move.use_specific_invoice_sequence and move.partner_id.invoice_sequence_id:
                    move.invoice_number_custom = move.partner_id.invoice_sequence_id.with_context(ir_sequence_date=move.date or fields.Date.context_today(move),ir_sequence_date_range=move.date or fields.Date.context_today(move)).next_by_id() 
                elif move.journal_id.invoice_sequence_id:
                    move.invoice_number_custom = move.journal_id.invoice_sequence_id.with_context(ir_sequence_date=move.date or fields.Date.context_today(move),ir_sequence_date_range=move.date or fields.Date.context_today(move)).next_by_id()
        return super(AccountMove, self)._post(soft=soft)

    @api.depends('partner_id', 'move_type', 'state')
    def _compute_use_specific_invoice_sequence(self):
        for move in self:
            move.use_specific_invoice_sequence = (move.partner_id.use_specific_invoice_sequence and move.move_type == 'out_invoice') or move.journal_id.invoice_sequence_id
    
    @api.depends('name', 'use_specific_invoice_sequence')
    def _compute_made_sequence_hole(self):
        super(AccountMove, self)._compute_made_sequence_hole()
        for move in self.filtered(lambda move: move.use_specific_invoice_sequence):
            move.made_sequence_hole = False


    @api.depends('posted_before', 'state', 'journal_id', 'date', 'move_type', 'payment_id', 'use_specific_invoice_sequence')
    def _compute_name(self):
        move_not_use_specific_sequence = self.filtered(lambda move: not move.use_specific_invoice_sequence)
        for move in self.filtered(lambda move: move.use_specific_invoice_sequence):
            
            if move.state == 'cancel':
                continue
            
            move_has_name = move.name and move.name != '/'
            invoice_number_custom = move.invoice_number_custom 
            move.name = invoice_number_custom or move.name or '/'
        super(AccountMove, move_not_use_specific_sequence)._compute_name()

    def _inverse_name(self):
        self = self.filtered(lambda move: not move.use_specific_invoice_sequence)
        if not self:
            return
        return super(AccountMove, self)._inverse_name()

    def _get_last_sequence_domain(self, relaxed=False):
        where_string, param = super(AccountMove, self)._get_last_sequence_domain(relaxed=relaxed)
        where_string += " AND use_specific_invoice_sequence is False"
        return where_string, param

    @api.onchange('term_condition_id')
    def onchange_term_condition_id(self):
        self.narration = self.term_condition_id.description


    def count_decimal_places(self,number):
    # Konversi angka menjadi string
        number_str = f"{number:.10f}".rstrip('0')  # Menghilangkan nol di akhir tanpa menghilangkan angka penting
        # Periksa apakah ada titik desimal
        if '.' in number_str:
            # Hitung panjang bagian setelah titik desimal
            decimal_places = len(number_str.split('.')[1])
        else:
            decimal_places = 0
        return min(decimal_places,3)