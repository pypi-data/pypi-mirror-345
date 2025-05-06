import json, datetime
from mt940.models import Amount


class MT940Encoder(json.JSONEncoder):
    DATE_FORMAT = "%Y-%m-%d"
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return {
                "_type": "date",
                "value": obj.strftime(self.DATE_FORMAT)
            }
        if isinstance(obj, Amount):
            return dict(
                _type='decimal',
                value=str(obj.amount)
                )
        return super().default(obj)
