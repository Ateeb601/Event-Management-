from odoo import models, fields

class EventAmenity(models.Model):
    _name = 'event.amenity'
    _description = 'Event Amenities'

    name = fields.Char('Name', required=True)
    type = fields.Char('Type', required=True)
    price = fields.Float('Price')
    image = fields.Binary('Image')
    description = fields.Text('Description')