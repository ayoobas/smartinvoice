from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, logout, login
from django.contrib import messages
from .models import Cropitem, Invoice, User
from django.utils import timezone
from django.core.files.base import ContentFile
import base64
import uuid
from django.db import IntegrityError
from io import BytesIO
from xhtml2pdf import pisa
import threading
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required

#To load the rates and display them
@login_required(login_url = 'login_def')
def home(request):
    items = Cropitem.objects.all()
    context = {
            'items':items
    }
    return render(request, 'index.html', context)

# for login
def login_def(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username = username , password = password)
        if user is not None:
            login(request, user)
            #messages.success(request, ("You have been logged in!"))
            return redirect('home')
        else:
            messages.warning(request, ("incorrect username or password!"))
            return redirect('login_def')
 
    return render(request, 'login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, ("You  logged out"))
    return redirect('login_def')

# To generate the invoice 
@login_required(login_url = 'login_def')
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


class StaffRegistration(View):
    def get(self, request):
        return render(request, 'staffregistration.html', locals())
    def post(self, request):
        # Handle the registration logic on POST requests
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')

           # Validate the form data
        if not username or not email or not password or not cpassword:
            messages.warning(request, "All fields are required.")
            return render(request, 'staffregistration.html', locals())
        
        if password != cpassword:
            messages.warning(request, "Passwords do not match.")
            return render(request, 'staffregistration.html', locals())
          # Check if a user with the same username or email already exists

        if User.objects.filter(email=email).exists():
            messages.warning(request, "Email already taken.")
            return render(request, 'staffregistration.html', locals())
        
        # Check if a user with the same username or email already exists
        if User.objects.filter(username=username).exists():
            messages.warning(request, "Username already taken.")
            return render(request, 'staffregistration.html', locals())
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Congratulations! Profile saved successfully.")
        return redirect('login_def')

#To send invoice as email
def send_invoice_background(invoice, subtotal, line_totals):
    # 1. Prepare HTML for the PDF
    html_context = {
        'invoice': invoice,
        'subtotal': subtotal,
        'line_totals': line_totals,
    }
    html_string = render_to_string('success.html', html_context)
    
    # 2. Create the PDF in memory (no need to save a file on disk)
    pdf_buffer = BytesIO()
    pisa.CreatePDF(BytesIO(html_string.encode("UTF-8")), dest=pdf_buffer)
    pdf_data = pdf_buffer.getvalue()

    # 3. Setup the Email
    subject = f"Invoice {invoice.invoice_number} from Obaz Grocery"
    email = EmailMessage(
        subject,
        "Thank you for shopping with us. \n"
        "Please find your attached invoice summary.",
        'Obaz Grocery <your-email@gmail.com>',
        [invoice.email],
    )
    
    # Attach the PDF
    email.attach(f"Invoice_{invoice.invoice_number}.pdf", pdf_data, 'application/pdf')

    # 4. Start the background thread
    email_thread = threading.Thread(target=email.send)
    email_thread.start()

#To view the invoice generated
#Input farm records
@login_required(login_url='user_login')
def view_invoice(request, pk):
    # 1. Fetch the invoice
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # 2. Fetch rates efficiently
    items_in_db = Cropitem.objects.all()
    rates = {item.name: item.rate for item in items_in_db}
    
    # 3. Calculate Line Totals (Required for both Template and Email)
    line_totals = {
        't': invoice.tomatoes * rates.get('Tomatoes', 0),
        'b': invoice.bell_pepper * rates.get('Bell_Pepper', 0),
        'c': invoice.cucumber * rates.get('Cucumber', 0),
        'a': invoice.abernero * rates.get('Abanero', 0),
    }
    
    # 4. Calculate Subtotal
    subtotal = sum(line_totals.values())

    # 5. TRIGGER BACKGROUND EMAIL
    # Note: We check 'invoice.name.email' because email is stored in CustomerInfo
    if invoice.email:
        send_invoice_background(invoice, subtotal, line_totals)

    # 6. Prepare context for the Success Page
    context = {
        'invoice': invoice,
        'line_totals': line_totals,
        'subtotal': subtotal,
        'rate_t': rates.get('Tomatoes', 0),
        'rate_b': rates.get('Bell_Pepper', 0),
        'rate_c': rates.get('Cucumber', 0),
        'rate_a': rates.get('Abanero', 0),
    }
    
    return render(request, 'success.html', context)


