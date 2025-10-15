from flask import Blueprint, request, jsonify
from extensions import db
from models import Event, Attendee
from import_handler import handle_csv_upload
from datetime import datetime

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/events', methods=['GET'])
def list_events():
    search = request.args.get('search')
    dateq = request.args.get('date')
    q = Event.query
    if search:
        q = q.filter(Event.title.ilike(f"%{search}%"))
    if dateq:
        try:
            dt = datetime.fromisoformat(dateq)
            q = q.filter(Event.date >= dt)
        except Exception:
            pass
    events = q.order_by(Event.date.asc()).all()
    return jsonify([e.to_dict() for e in events])

@api.route('/events', methods=['POST'])
def create_event():
    data = request.json or {}
    title = data.get('title')
    if not title:
        return jsonify({'error': 'title required'}), 400
    try:
        date = datetime.fromisoformat(data.get('date')) if data.get('date') else None
    except Exception:
        return jsonify({'error': 'invalid date format'}), 400

    ev = Event(title=title, description=data.get('description'), date=date, location=data.get('location'), capacity=data.get('capacity') or 0)
    db.session.add(ev)
    db.session.commit()
    return jsonify(ev.to_dict()), 201

@api.route('/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    ev = Event.query.get_or_404(event_id)
    return jsonify(ev.to_dict())

@api.route('/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    ev = Event.query.get_or_404(event_id)
    data = request.json or {}
    ev.title = data.get('title', ev.title)
    ev.description = data.get('description', ev.description)
    try:
        ev.date = datetime.fromisoformat(data.get('date')) if data.get('date') else ev.date
    except Exception:
        return jsonify({'error': 'invalid date format'}), 400
    ev.location = data.get('location', ev.location)
    ev.capacity = data.get('capacity', ev.capacity)
    db.session.commit()
    return jsonify(ev.to_dict())

@api.route('/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    ev = Event.query.get_or_404(event_id)
    db.session.delete(ev)
    db.session.commit()
    return jsonify({'status': 'deleted'})

@api.route('/events/<int:event_id>/attendees', methods=['GET'])
def list_attendees(event_id):
    ev = Event.query.get_or_404(event_id)
    attendees = [a.to_dict() for a in ev.attendees]
    return jsonify(attendees)

@api.route('/events/<int:event_id>/attendees', methods=['POST'])
def register_attendee(event_id):
    ev = Event.query.get_or_404(event_id)
    data = request.json or {}
    name = data.get('name')
    if not name:
        return jsonify({'error': 'name required'}), 400
    tickets = int(data.get('tickets', 1))
    sold = sum(a.tickets for a in ev.attendees)
    available = max(ev.capacity - sold, 0)
    if tickets > available:
        return jsonify({'error': 'Not enough tickets available', 'available': available}), 400
    attendee = Attendee(name=name, email=data.get('email'), phone=data.get('phone'), tickets=tickets, event=ev)
    db.session.add(attendee)
    db.session.commit()
    return jsonify(attendee.to_dict()), 201

@api.route('/attendees/<int:attendee_id>', methods=['PUT'])
def update_attendee(attendee_id):
    a = Attendee.query.get_or_404(attendee_id)
    data = request.json or {}
    a.name = data.get('name', a.name)
    a.email = data.get('email', a.email)
    a.phone = data.get('phone', a.phone)
    try:
        a.tickets = int(data.get('tickets', a.tickets))
    except Exception:
        pass
    db.session.commit()
    return jsonify(a.to_dict())

@api.route('/events/<int:event_id>/tickets', methods=['GET'])
def tickets_report(event_id):
    ev = Event.query.get_or_404(event_id)
    sold = sum(a.tickets for a in ev.attendees)
    available = max(ev.capacity - sold, 0)
    try:
        price = float(request.args.get('price', 0))
    except Exception:
        price = 0
    revenue = sold * price
    return jsonify({'sold': sold, 'available': available, 'revenue': revenue})

@api.route('/import/events', methods=['POST'])
def import_events():
    if 'file' not in request.files:
        return jsonify({'error': 'file missing'}), 400
    f = request.files['file']
    result = handle_csv_upload(f)
    return jsonify(result)
