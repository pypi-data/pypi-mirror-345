from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from app.models.contact import Contact
from app.models import db

class ContactSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Contact
        include_relationships = True
        load_instance = True
        sqla_session = db.session

    created_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S")
    updated_at = fields.DateTime(format="%Y-%m-%d %H:%M:%S")