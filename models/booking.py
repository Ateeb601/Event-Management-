from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class EventBooking(models.Model):
    _name = 'event.booking'
    _description = 'Event Booking Form'

    name = fields.Char('Customer Name', required=True)
    phone = fields.Char('Phone Number', required=True)
    start_time = fields.Datetime('Event Start Time', required=True)
    end_time = fields.Datetime('Event End Time', required=True)
    booking_date = fields.Date('Booking Date', required=True)
    event_type_id = fields.Many2one('event.type', string='Event Type', required=True)
    event_category_id = fields.Many2one('event.category', string='Event Category', required=True)
    hall_id = fields.Many2one('event.hall', string='Hall', required=True)

    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')

    amenities = fields.Many2many('event.amenity', string='Amenities')
    amenities_total = fields.Float('Amenities Total', compute='_compute_amenities_total', store=True)
    total_person = fields.Integer('Total Person', default=1)

    # Menu dishes integration
    selected_dishes = fields.Many2many('menu.dishes', 'booking_dishes_rel',
                                       'booking_id', 'dish_id', string='Selected Dishes')
    available_meal_packages = fields.Many2many('menu.meal', string='Available Meal Packages',
                                               compute='_compute_available_meal_packages')
    excluded_meal_packages = fields.Many2many('menu.meal', 'booking_excluded_meal_rel',
                                              'booking_id', 'meal_id', string='Excluded Meal Packages')
    selected_meal_packages = fields.Many2many('menu.meal', 'booking_meal_rel',
                                              'booking_id', 'meal_id', string='Selected Meal Packages')
    meat_type_filter = fields.Selection([
        ('chicken', 'Chicken'),
        ('mutton', 'Mutton'),
        ('beef', 'Beef')
    ], string='Meat Type Preference')

    dishes_per_person = fields.Float('Dishes Per Person', compute='_compute_dishes_per_person', store=True)
    total_dishes_cost = fields.Float('Total Dishes Cost', compute='_compute_total_dishes_cost', store=True)
    total_meal_price = fields.Float('Total Meal Price', compute='_compute_total_meal_price', store=True)
    grand_total = fields.Float('Grand Total', compute='_compute_grand_total', store=True)

    # ==================== COMPUTED FIELDS ====================

    @api.depends('amenities.price')
    def _compute_amenities_total(self):
        """Calculate total cost of selected amenities for the booking"""
        for record in self:
            record.amenities_total = sum(record.amenities.mapped('price'))

    @api.depends('selected_dishes.price', 'selected_meal_packages.total_meal_price')
    def _compute_dishes_per_person(self):
        """Calculate total cost of selected dishes and meal packages per person"""
        for record in self:
            # Calculate dishes cost
            dishes_total = sum(record.selected_dishes.mapped('price')) or 0

            # Calculate meal packages cost (per person)
            meal_packages_total = sum(record.selected_meal_packages.mapped('total_meal_price')) or 0

            # Total per person cost
            record.dishes_per_person = dishes_total + meal_packages_total

    @api.depends('dishes_per_person', 'total_person')
    def _compute_total_dishes_cost(self):
        """Calculate total dishes cost for all persons"""
        for record in self:
            record.total_dishes_cost = record.dishes_per_person * record.total_person

    @api.depends('selected_meal_packages.total_meal_price', 'total_person')
    def _compute_total_meal_price(self):
        """Calculate total meal package cost (packages * persons)"""
        for record in self:
            meal_packages_total = sum(record.selected_meal_packages.mapped('total_meal_price')) or 0
            record.total_meal_price = meal_packages_total * record.total_person

    @api.depends('total_dishes_cost', 'amenities_total')
    def _compute_grand_total(self):
        """Calculate grand total (dishes + meals + amenities)"""
        for record in self:
            record.grand_total = record.total_dishes_cost + record.amenities_total

    @api.depends('meat_type_filter', 'excluded_meal_packages')
    def _compute_available_meal_packages(self):
        """Compute available meal packages based on meat type filter and excluded packages"""
        for record in self:
            domain = [('active', '=', True)]
            if record.meat_type_filter:
                domain.append(('meat_type', '=', record.meat_type_filter))
            if record.excluded_meal_packages:
                domain.append(('id', 'not in', record.excluded_meal_packages.ids))
            record.available_meal_packages = self.env['menu.meal'].search(domain)

    # ==================== ONCHANGE METHODS ====================

    @api.onchange('total_person')
    def _onchange_total_person(self):
        """Auto-suggest suitable hall based on person count when total_person changes"""
        if self.total_person:
            suitable_hall = self.env['event.hall'].search([
                ('capacity', '>=', self.total_person)
            ], order='capacity asc', limit=1)
            if suitable_hall:
                self.hall_id = suitable_hall.id

    # ==================== VALIDATION METHODS ====================

    @api.constrains('start_time', 'end_time', 'hall_id', 'booking_date')
    def _check_hall_availability(self):
        """Validate hall availability - prevent double booking of same hall at same time"""
        for record in self:
            if record.start_time >= record.end_time:
                raise ValidationError("End time must be after start time")

            existing = self.search([
                ('hall_id', '=', record.hall_id.id),
                ('booking_date', '=', record.booking_date),
                ('status', '=', 'confirmed'),
                ('id', '!=', record.id),
                '|',
                '&', ('start_time', '<=', record.start_time), ('end_time', '>', record.start_time),
                '&', ('start_time', '<', record.end_time), ('end_time', '>=', record.end_time)
            ])
            if existing:
                raise ValidationError(f"Hall {record.hall_id.name} is already booked for this time slot")

    # ==================== BOOKING STATUS ACTIONS ====================

    def action_confirm(self):
        """Confirm the booking - changes status from draft to confirmed"""
        for rec in self:
            rec.status = 'confirmed'

    def action_cancel(self):
        """Cancel the booking - changes status to cancelled (preserves record)"""
        for rec in self:
            rec.status = 'cancelled'

    # ==================== MEAT TYPE FILTER ACTIONS ====================

    def action_set_chicken(self):
        """Set meat type filter to chicken - shows only chicken meal packages"""
        self.meat_type_filter = 'chicken'

    def action_set_mutton(self):
        """Set meat type filter to mutton - shows only mutton meal packages"""
        self.meat_type_filter = 'mutton'

    def action_set_beef(self):
        """Set meat type filter to beef - shows only beef meal packages"""
        self.meat_type_filter = 'beef'

    # ==================== MEAL PACKAGE MANAGEMENT ====================
    # In your event_booking.py model, update these methods:

    # ==================== MEAL PACKAGE MANAGEMENT ====================

    def action_select_meal_from_kanban(self):
        """Select meal package from kanban view"""
        meal_id = self.env.context.get('meal_id')
        if meal_id:
            self.write({
                'selected_meal_packages': [(4, meal_id)],
                'excluded_meal_packages': [(3, meal_id)]
            })
        return False  # Changed from True to False

    def action_remove_meal_from_kanban(self):
        """Remove meal package from kanban view"""
        meal_id = self.env.context.get('meal_id')
        if meal_id:
            self.write({
                'selected_meal_packages': [(3, meal_id)],
                'excluded_meal_packages': [(4, meal_id)]
            })
        return False  # Changed from True to False

    def action_remove_dish(self):
        """Remove dish from selected dishes"""
        dish_id = self.env.context.get('dish_id')
        if dish_id:
            self.selected_dishes = [(3, dish_id)]
        return False  # Changed from True to False

    def action_open_meal_packages(self):
        """Open meal packages selection wizard"""
        domain = [('active', '=', True)]
        if self.meat_type_filter:
            domain.append(('meat_type', '=', self.meat_type_filter))

        return {
            'name': 'Select Meal Package',
            'type': 'ir.actions.act_window',
            'res_model': 'menu.meal',
            'view_mode': 'kanban,list,form',
            'target': 'new',
            'context': {'default_booking_id': self.id},
            'domain': domain,
        }

    # ==================== DEBUG METHODS ====================

    def check_calculations(self):
        """Debug method to check current calculations"""
        self._compute_dishes_per_person()
        self._compute_total_dishes_cost()
        self._compute_total_meal_price()
        self._compute_grand_total()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Calculation Debug',
                'message': f"""
                Per Person: {self.dishes_per_person}
                Total Persons: {self.total_person}
                Total Dishes Cost: {self.total_dishes_cost}
                Total Meal Price: {self.total_meal_price}
                Amenities Total: {self.amenities_total}
                Grand Total: {self.grand_total}
                """,
                'sticky': True,
            }
        }
