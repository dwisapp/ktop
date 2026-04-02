from odoo import models, fields, api, _

class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    # hr_kategori_pph_id = fields.Many2one('hr.kategori.pph', string='Kategori PPh')
    hr_kategori_ter_id = fields.Many2one('hr.kategori.ter', string='Kategori Ter', store=True, readonly=False)

    @api.depends('marital', 'children')
    def _compute_kategori_ter(self):
        kategori_ter = self.env['hr.kategori.ter'].search([])
        for employee in self:
            if not employee.marital:
                continue
            ter_dict = {}
            employee_children = employee.children
            if employee.marital == 'married':
                ter_dict = {
                    0 : "TER A",
                    1 : "TER A",
                    2 : "TER B",
                    3 : "TER C",
                }
                
                if employee_children > 3:
                    employee_children = 3
                

            else:
                ter_dict = {
                    0 : "TER A",
                    1 : "TER B",
                    2 : "TER B",
                }
                if employee_children > 2:
                    employee_children = 2

            employee.hr_kategori_ter_id = kategori_ter.filtered(lambda x: x.name == ter_dict[employee_children])

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # hr_kategori_pph_id = fields.Many2one('hr.kategori.pph', string='Kategori PPh')
    hr_kategori_ter_id = fields.Many2one('hr.kategori.ter', string='Kategori Ter', compute='_compute_kategori_ter', store=True, readonly=False)

    @api.depends('marital', 'children')
    def _compute_kategori_ter(self):
        kategori_ter = self.env['hr.kategori.ter'].search([])
        for employee in self:
            if not employee.marital:
                continue
            ter_dict = {}
            employee_children = employee.children
            if employee.marital == 'married':
                ter_dict = {
                    0 : "TER A",
                    1 : "TER A",
                    2 : "TER B",
                    3 : "TER C",
                }
                
                if employee_children > 3:
                    employee_children = 3
                

            else:
                ter_dict = {
                    0 : "TER A",
                    1 : "TER B",
                    2 : "TER B",
                }
                if employee_children > 2:
                    employee_children = 2

            employee.hr_kategori_ter_id = kategori_ter.filtered(lambda x: x.name == ter_dict[employee_children])

    # @api.depends('hr_kategori_pph_id')
    # def _compute_kategori_ter(self):
    #     for rec in self:
    #         rec.hr_kategori_ter_id = rec.hr_kategori_pph_id.hr_kategori_ter_id.id if rec.hr_kategori_pph_id else False
    