from app.models import db
from app.models.mixin import TimestampMixin

class Example(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    street_address = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    county = db.Column(db.String(120), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<Contact {self.first_name} {self.last_name}>'