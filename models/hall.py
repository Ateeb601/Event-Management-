from odoo import models, fields

class EventHall(models.Model):
    _name = 'event.hall'
    _description = 'Event Hall'

    name = fields.Char('Hall Name', required=True)
    image = fields.Binary('Image')
    capacity = fields.Integer('Capacity')
    chairs = fields.Integer('Number of Chairs')
    tables = fields.Integer('Number of Tables')
    facilities = fields.Selection([
        ('ac', 'Air Conditioning'),
        ('parking', 'Parking'),
        ('stage', 'Stage'),
        ('sound', 'Sound System'),
        ('wifi', 'WiFi')
    ], string='Facilities')