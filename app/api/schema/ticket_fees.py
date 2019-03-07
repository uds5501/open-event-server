from marshmallow import validate, validates_schema
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from sqlalchemy.orm.exc import NoResultFound
from app.api.helpers.static import PAYMENT_CURRENCY_CHOICES
from app.api.helpers.utilities import dasherize
from app.api.helpers.exceptions import ConflictException, UnprocessableEntity
from app.models.ticket_fee import TicketFees


class TicketFeesSchema(Schema):
    """
    Api schema for ticket_fee Model
    """
    class Meta:
        """
        Meta class for image_size Api Schema
        """
        type_ = 'ticket-fee'
        self_view = 'v1.ticket_fee_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    @validates_schema(pass_original=True)
    def validate_currency_country(self, data, original_data):
        if 'country' in data and 'currency' in data:
            if data['country'] and data['currency']:
                try:
                    TicketFees.query.filter_by(country=data['country'], currency=data['currency']).one()
                except NoResultFound:
                    pass
                else:
                    # modifications for PATCH request
                    if 'id' not in original_data:
                        raise ConflictException(
                            {'pointer': ''},
                            "({}-{}) Combination already exists".format(data['currency'], data['country']))
            else:
                raise UnprocessableEntity({'source': ''}, "Country or Currency cannot be NULL")
        else:
            raise UnprocessableEntity({'source': ''}, "Country or Currency Attribute is missing")

    id = fields.Integer(dump_only=True)
    currency = fields.Str(validate=validate.OneOf(choices=PAYMENT_CURRENCY_CHOICES), allow_none=True)
    country = fields.String(allow_none=True)
    service_fee = fields.Float(validate=lambda n: n >= 0, allow_none=True)
    maximum_fee = fields.Float(validate=lambda n: n >= 0, allow_none=True)
