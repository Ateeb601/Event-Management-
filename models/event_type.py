from odoo import models, fields

class EventType(models.Model):
    _name = 'event.type'
    _description = 'Event Type'

    name = fields.Char('Event Type', required=True)
    code = fields.Char('Code', required=True, help='Code for sequence generation (e.g., WED, CONF)')
    category_ids = fields.One2many('event.category', 'event_type_id', string='Categories')

class EventCategory(models.Model):
    _name = 'event.category'
    _description = 'Event Category'

    name = fields.Char('Category Name', required=True)
    event_type_id = fields.Many2one('event.type', string='Event Type', required=True)