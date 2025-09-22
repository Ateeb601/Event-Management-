from odoo import models, fields, api


class MenuMeal(models.Model):
    _name = 'menu.meal'
    _description = 'Menu Meal Package'
    _order = 'event_category_id, name'

    name = fields.Char('Meal Package Name', required=True)
    event_category_id = fields.Many2one('event.category', string='Event Category')
    meat_type = fields.Selection([
        ('chicken', 'Chicken'),
        ('mutton', 'Mutton'),
        ('beef', 'Beef')
    ], string='Meat Type')
    meat_dishes = fields.Many2many('menu.dishes', 'meal_meat_rel', 'meal_id', 'dish_id', string='Meat Dishes')

    # Chicken Dishes (Qorma/Karahi/Badami)
    chicken_curry_ids = fields.Many2many('menu.dishes', 'meal_chicken_rel', 'meal_id', 'dish_id',
                                         string='Chicken Curry')

    # Mutton Dishes
    mutton_curry_ids = fields.Many2many('menu.dishes', 'meal_mutton_rel', 'meal_id', 'dish_id',
                                        string='Mutton Curry')

    # Beef Dishes
    beef_curry_ids = fields.Many2many('menu.dishes', 'meal_beef_rel', 'meal_id', 'dish_id',
                                      string='Beef Curry')

    # Rice Dishes (Biryani/Pulao)
    rice_dish_ids = fields.Many2many('menu.dishes', 'meal_rice_rel', 'meal_id', 'dish_id',
                                     string='Rice Dish')

    # Desserts (Kheer/Firni/Kulfa/Zarda)
    dessert_ids = fields.Many2many('menu.dishes', 'meal_dessert_rel', 'meal_id', 'dish_id',
                                   string='Dessert')

    # Salads (Fresh/Kachumar, Zeera Raita/Mint Raita)
    salad_ids = fields.Many2many('menu.dishes', 'meal_salad_rel', 'meal_id', 'dish_id',
                                 string='Salad')

    # Drinks (Soft Drinks, Mineral Water)
    drink_ids = fields.Many2many('menu.dishes', 'meal_drink_rel', 'meal_id', 'dish_id',
                                 string='Drink')

    # Bread (Live Roghani Naan)
    bread_ids = fields.Many2many('menu.dishes', 'meal_bread_rel', 'meal_id', 'dish_id',
                                 string='Bread')

    # Computed fields
    total_meal_price = fields.Float('Total Price', store=True)
    description = fields.Text('Description')
    active = fields.Boolean('Active', default=True)
    is_selected = fields.Boolean('Is Selected', default=False)

    # ==================== ONCHANGE METHODS ====================
    
    @api.onchange('meat_type')
    def _onchange_meat_type(self):
        """Auto-populate meat dishes based on selected meat type when meat_type changes"""
        if self.meat_type == 'chicken':
            self.meat_dishes = self.chicken_curry_ids
        elif self.meat_type == 'mutton':
            self.meat_dishes = self.mutton_curry_ids
        elif self.meat_type == 'beef':
            self.meat_dishes = self.beef_curry_ids
        else:
            self.meat_dishes = False


    

    # ==================== BOOKING INTEGRATION ACTIONS ====================
    
    def action_add_to_booking(self):
        """Add meal package to booking from wizard popup - closes wizard after selection"""
        booking_id = self.env.context.get('default_booking_id')
        if booking_id:
            booking = self.env['event.booking'].browse(booking_id)
            booking.selected_meal_package = self.id
            return {'type': 'ir.actions.act_window_close'}
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': 'Please select meal package from booking form',
                'type': 'warning',
            }
        }

    def action_select_meal_package(self):
        """Select meal package from available packages"""
        # Try multiple ways to find the booking
        booking = None
        
        # Method 1: From context
        booking_id = self.env.context.get('default_booking_id') or self.env.context.get('active_id')
        if booking_id and self.env.context.get('active_model') == 'event.booking':
            booking = self.env['event.booking'].browse(booking_id)
        
        # Method 2: Find booking that has this meal in available packages
        if not booking:
            booking = self.env['event.booking'].search([('available_meal_packages', 'in', self.id)], limit=1)
        
        # Method 3: Find any draft booking (fallback)
        if not booking:
            booking = self.env['event.booking'].search([('status', '=', 'draft')], limit=1)
            
        if booking:
            booking.write({
                'selected_meal_packages': [(4, self.id)],
                'selected_meal_package': self.id
            })
        return True



    # ==================== MEAL PACKAGE MANAGEMENT ====================
    
    def action_cancel_meal_package(self):
        """Remove this meal package from the current booking selection"""
        booking_id = self.env.context.get('active_id')
        if booking_id:
            booking = self.env['event.booking'].browse(booking_id)
            booking.selected_meal_packages = [(3, self.id)]
            if booking.selected_meal_package and booking.selected_meal_package.id == self.id:
                booking.selected_meal_package = False
        return {'type': 'ir.actions.act_window_close'}

    def action_select_meal_package(self):
        """Select this meal package for the current booking"""
        booking_id = self.env.context.get('active_id')
        if booking_id:
            booking = self.env['event.booking'].browse(booking_id)
            booking.selected_meal_packages = [(4, self.id)]
            booking.selected_meal_package = self.id
            # Trigger recomputation of price fields
            booking._compute_dishes_per_person()
            booking._compute_total_dishes_cost()
            booking._compute_grand_total()
        return {'type': 'ir.actions.act_window_close'}

    def action_edit_meal(self):
        """Open meal package form in edit mode for modification"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'menu.meal',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

