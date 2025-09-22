from odoo import models, fields, api


class MenuDishes(models.Model):
    _name = 'menu.dishes'
    _description = 'Menu Dishes'
    _order = 'meal_type, sequence, name'

    name = fields.Char('Dish Name', required=True)
    description = fields.Text('Description')
    dish_category_id = fields.Many2one('dish.category', string='Dish Category', required=True)
    price = fields.Float('Price', related='dish_category_id.price', store=True, readonly=True)
    image = fields.Binary('Image')
    meal_type = fields.Selection([
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snacks', 'Snacks'),
        ('beverages', 'Beverages')
    ], string='Meal Type', required=True)
    
    meat_type = fields.Selection([
        ('chicken', 'Chicken'),
        ('mutton', 'Mutton'),
        ('beef', 'Beef'),
        ('fish', 'Fish'),
        ('vegetarian', 'Vegetarian')
    ], string='Meat Type')
    
    dish_category = fields.Selection([
        ('starter', 'Starter'),
        ('main_course', 'Main Course'),
        ('dessert', 'Dessert'),
        ('soup', 'Soup'),
        ('salad', 'Salad'),
        ('rice', 'Rice'),
        ('bread', 'Bread')
    ], string='Dish Category')
    
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)
    is_vegetarian = fields.Boolean('Vegetarian')
    is_spicy = fields.Boolean('Spicy')
    preparation_time = fields.Integer('Preparation Time (minutes)')
    
    # Booking integration
    booking_ids = fields.Many2many('event.booking', 'booking_dishes_rel', 
                                   'dish_id', 'booking_id', string='Bookings')
    
    @api.onchange('meat_type')
    def _onchange_meat_type(self):
        if self.meat_type == 'vegetarian':
            self.is_vegetarian = True
        else:
            self.is_vegetarian = False
    
    @api.model
    def get_dishes_by_meal(self, meal_type):
        """Get dishes filtered by meal type for booking form"""
        return self.search([('meal_type', '=', meal_type), ('active', '=', True)])
    
    def action_add_to_booking(self):
        """Add dish to current booking context"""
        booking_id = self.env.context.get('default_booking_id')
        if booking_id:
            booking = self.env['event.booking'].browse(booking_id)
            booking.selected_dishes = [(4, self.id)]
            return {'type': 'ir.actions.act_window_close'}
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': 'Please select dishes from booking form',
                'type': 'warning',
            }
        }
    
    def action_remove_dish(self):
        """Remove dish from booking"""
        booking = self.env['event.booking'].search([('selected_dishes', 'in', self.id)], limit=1)
        if booking:
            booking.selected_dishes = [(3, self.id)]
        return True