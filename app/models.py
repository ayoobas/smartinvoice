from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid

def validate_image_size(image):
    max_size = 0.5 * 1024 * 1024  # 1 MB
    if image.size > max_size:
        raise ValidationError("Image file too large (max 500KB allowed).")

def validate_not_future(value):
    if value > timezone.now().date():
        raise ValidationError("Date cannot be in the future.")


class Cropitem(models.Model):
    name = models.CharField( max_length=30)
    rate = models.PositiveIntegerField(default=0)
  
    class Meta:
        verbose_name = "Cropitem"
        verbose_name_plural = "Cropitem"  # Prevents Django from adding "s"

    def __str__(self):
        return str(self.name)


class Invoice(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)  
    name = models.CharField( max_length=30)
    address = models.CharField( max_length=40, blank=True, null=True)
    phone_no = models.CharField(max_length=20, blank=True, null=True, unique=True)
    email = models.EmailField( max_length=254, blank=True, null=True, unique=True)
  
    tomatoes = models.IntegerField(default =0 )
    bell_pepper = models.IntegerField(default =0 )
    cucumber = models.IntegerField(default =0 )
    abernero = models.IntegerField(default =0 )
    discount = models.IntegerField(default =0 )
    total_price = models.PositiveIntegerField(default=0)

    invoice_number = models.CharField(max_length=20, unique=True, editable=False)
    created_at = models.DateField(null=True, blank=True, validators=[validate_not_future])
    image = models.ImageField( validators=[validate_image_size],  upload_to = 'signatures', blank=True)

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



