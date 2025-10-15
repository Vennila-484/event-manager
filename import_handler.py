import csv
import io
from datetime import datetime
from models import Event
from extensions import db

DATE_FORMATS = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d", "%d-%m-%Y %H:%M", "%d-%m-%Y"]

def parse_date(value):
    if not value:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value.strip(), fmt)
        except Exception:
            continue
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None

def handle_csv_upload(file_storage):
    content = file_storage.stream.read()
    if isinstance(content, bytes):
        content = content.decode('utf-8', errors='replace')
    stream = io.StringIO(content)
    reader = csv.DictReader(stream)
    rows = []
    preview = []
    errors = []
    created = 0

    for i, row in enumerate(reader, start=1):
        title = row.get('Event Title') or row.get('Title') or row.get('title')
        description = row.get('Description') or row.get('description')
        date_raw = row.get('Date') or row.get('date')
        location = row.get('Location') or row.get('location')
        capacity_raw = row.get('Capacity') or row.get('capacity') or '0'

        if not title or not date_raw:
            errors.append({'row': i, 'error': 'Missing title or date'})
            continue

        date = parse_date(date_raw)
        if date is None:
            errors.append({'row': i, 'error': f'Unrecognized date: {date_raw}'})
            continue

        try:
            capacity = int(float(capacity_raw))
        except Exception:
            capacity = 0

        ev = Event(title=title.strip(), description=description, date=date, location=location, capacity=capacity)
        db.session.add(ev)
        rows.append({'title': ev.title, 'date': ev.date.isoformat(), 'location': ev.location, 'capacity': ev.capacity})
        preview.append({'title': title, 'date': date.isoformat(), 'location': location, 'capacity': capacity})
        created += 1

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        errors.append({'error': 'DB commit failed', 'detail': str(e)})

    return {'rows': rows, 'preview': preview, 'created': created, 'errors': errors}
