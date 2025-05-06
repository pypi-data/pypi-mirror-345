import hashlib
from django.db import models
from .json import MT940Encoder


class OrderAccount(models.Model):
    name = models.CharField(max_length=255, unique=True)
    iban = models.CharField(max_length=255, unique=True)
    bic = models.CharField(max_length=255)


class BankStatement(models.Model):
    order_account = models.ForeignKey(OrderAccount, models.CASCADE)
    applicant_name = models.CharField(max_length=255)
    applicant_iban = models.CharField(max_length=255)
    applicant_bic = models.CharField(max_length=255)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    currency = models.CharField(max_length=255)
    posting_text = models.CharField(max_length=255)
    purpose = models.TextField()
    additional_purpose = models.TextField()
    entry_date = models.DateField()
    date = models.DateField()
    data = models.JSONField(encoder=MT940Encoder)
    checksum = models.CharField(max_length=255)

    def get_checksum(self):
        sorted_data = sorted((k, v) for k, v in self.data.items())
        reference = str(sorted_data).encode('utf8')
        return hashlib.md5(reference    ).hexdigest()

    def save(self, *args, **kwargs):
        self.checksum = self.get_checksum()
        super().save(*args, **kwargs)
