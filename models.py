from datetime import datetime
from extensions import db

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    capacity = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attendees = db.relationship('Attendee', backref='event', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'date': self.date.isoformat() if self.date else None,
            'location': self.location,
            'capacity': self.capacity,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Attendee(db.Model):
    __tablename__ = 'attendees'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200))
    phone = db.Column(db.String(80))
    tickets = db.Column(db.Integer, default=1)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'tickets': self.tickets,
            'registered_at': self.registered_at.isoformat(),
            'event_id': self.event_id
        }
