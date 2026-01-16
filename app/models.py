from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid

class Croprate(models.Model):
    tomato_rate = models.PositiveIntegerField(default=0)
    bellpepper_rate = models.PositiveIntegerField(default=0)
    cucumber_rate = models.PositiveIntegerField(default=0)
    abernero_rate = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Croprate"
        verbose_name_plural = "Croprate"  # Prevents Django from adding "s"

    def __str__(self):
        return str(self.tomato_rate)


class Invoice(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)  
    name = models.CharField( max_length=30)
    address = models.CharField( max_length=40, blank=True, null=True)
    phone_no = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField( max_length=30, blank=True, null=True)
  
    tomatoes = models.IntegerField(default =0 )
    bell_pepper = models.IntegerField(default =0 )
    cucumber = models.IntegerField(default =0 )
    abernero = models.IntegerField(default =0 )
    # crop_rate = models.ForeignKey(Croprate, on_delete=models.CASCADE)
    total_price = models.PositiveIntegerField(default=0)

    invoice_number = models.CharField(max_length=20, unique=True, editable=False)
    created_at = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoice"  # Prevents Django from adding "s"    

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generates a short, unique 8-character code
            unique_id = str(uuid.uuid4()).upper()[:8]
            year = timezone.now().year
            self.invoice_number = f"OBAZ-{year}-{unique_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



