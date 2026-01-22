from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from .models import Cropitem, Invoice
from django.utils import timezone
from django.core.files.base import ContentFile
import base64
import uuid
from django.db import IntegrityError

#To load the rates and display them
def home(request):
    items = Cropitem.objects.all()
    context = {
            'items':items
    }
    return render(request, 'index.html', context)


# To generate the invoice 
def generate_invoice(request):
    if request.method == "POST":
        # 1. Capture Basic Customer Info
        fname = request.POST.get("fname")
        address = request.POST.get("address")
        phoneno = request.POST.get("phoneno")
        email = request.POST.get("email")
        createdate = request.POST.get("createdate")

     
        # 2.1 Capture Quantities (Default to 0 if empty)
        qty_tomatoes = int(request.POST.get("Tomatoes") or 0)
        qty_bell_pepper = int(request.POST.get("Bell_Pepper") or 0)
        qty_cucumber = int(request.POST.get("Cucumber") or 0)
        qty_habanero = int(request.POST.get("Abanero") or 0)
        discount = int(request.POST.get("discount") or 0)



        # 2. THE CONDITION: Check if total items are greater than 0
        if qty_tomatoes == 0 and qty_bell_pepper == 0 and qty_cucumber == 0 and qty_habanero == 0:
            messages.warning(request, "Error: You must enter at least one item quantity to generate an invoice.")
            return render(request, 'index.html', {'items': Cropitem.objects.all()})
        # 3. Dynamic Price Calculation from Database
        # We fetch all rates into a dictionary for easy lookup
        items_in_db = Cropitem.objects.all()
        rates = {item.name: item.rate for item in items_in_db}

        subtotal = (
            (qty_tomatoes * rates.get('Tomatoes', 0)) +
            (qty_bell_pepper * rates.get('Bell_Pepper', 0)) +
            (qty_cucumber * rates.get('Cucumber', 0)) +
            (qty_habanero * rates.get('Abanero', 0))
        )
        final_total = subtotal - discount

     

        # 5. Handle Digital Signature (Base64 String to File)
        signature_data = request.POST.get("signature_data")
        signature_file = None
        
        if signature_data and "base64," in signature_data:
            # Strip the header (data:image/png;base64,)
            format, imgstr = signature_data.split('base64,')
            ext = format.split('/')[-1].split(';')[0] # Get extension (e.g., png)
            
            # Create a ContentFile that Django can save to an ImageField
            signature_file = ContentFile(
                base64.b64decode(imgstr), 
                name=f"signature_{uuid.uuid4().hex[:6]}.{ext}"
            )

        # 6. Save to Invoice Model
        # invoice_number is generated automatically by your model's save() method
        try:
             new_invoice = Invoice.objects.create(
             name=fname,
            address=address,
            phone_no=phoneno,
            email=email,
            tomatoes=qty_tomatoes,
            bell_pepper=qty_bell_pepper,
            cucumber=qty_cucumber,
            abernero=qty_habanero,
            discount=discount,
            total_price=final_total,
            image=signature_file,   # The uploaded photo
        
            created_at=createdate if createdate else timezone.now().date()
        )
             # If successful, go to the success page
               # 7. Redirect or Render Success Page
             messages.success(request, "✅ Records saved successfully!")
             return redirect('view_invoice', pk=new_invoice.pk)
        except IntegrityError:
            # If the database blocks the save due to unique=True
            messages.warning(request, "This Email or Phone Number is already registered. Please use a different one.")

      

    # GET Request: Load items for the table and show the form
    items = Cropitem.objects.all()
    return render(request, 'index.html', {'items': items})

#To view the invoice generated

def view_invoice(request, pk):
    # This fetches only ONE invoice by its ID, or shows a 404 error if not found
    items_in_db = Cropitem.objects.all()
    rates = {item.name: item.rate for item in items_in_db}
    rate_t = rates.get('Tomatoes', 0)
    rate_b =  rates.get('Bell_Pepper', 0)
    rate_c = rates.get('Cucumber', 0)
    rate_a = rates.get('Abanero', 0)

    invoice = get_object_or_404(Invoice, pk=pk)

    print('invoice',invoice)
    
    context = {
        'invoice': invoice,
        'rate_t':rate_t,
        'rate_b':rate_b,
        'rate_c':rate_c,
        'rate_a':rate_a
    }
    return render(request, 'success.html', context)



