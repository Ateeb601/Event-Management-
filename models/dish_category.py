from odoo import models, fields, api


class DishCategory(models.Model):
    _name = 'dish.category'
    _description = 'Dish Category'
    _order = 'sequence, name'

    name = fields.Char('Category Name', required=True)
    price = fields.Float('Category Price', required=True)
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)
    description = fields.Text('Description')
    
    # Related dishes
    dish_ids = fields.One2many('menu.dishes', 'dish_category_id', string='Dishes')
    dish_count = fields.Integer('Dish Count', compute='_compute_dish_count')
    
    @api.depends('dish_ids')
    def _compute_dish_count(self):
        for record in self:
            record.dish_count = len(record.dish_ids)
    
    def action_view_dishes(self):
        return {
            'name': 'Dishes',
            'type': 'ir.actions.act_window',
            'res_model': 'menu.dishes',
            'view_mode': 'list,form',
            'domain': [('dish_category_id', '=', self.id)],
        }