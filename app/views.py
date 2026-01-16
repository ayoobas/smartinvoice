from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from .models import Croprate, Invoice

#To load the rates and display them
def home(request):
    rate = Croprate.objects.all()
    context = {
            'rate':rate
    }
    return render(request, 'index.html', context)

#to do the calculation
def pricecalculation(request):
 
    if request.method == "POST":
        fname = request.POST.get("fname")
        address =  request.POST.get("address")

        phoneno = request.POST.get("phoneno")
        email = request.POST.get("email")
        
        tomatoes = request.POST.get("tomatoes")
        
        bell_pepper = request.POST.get("bell_pepper")
        cucumber = request.POST.get("cucumber")
        abernero = request.POST.get("abernero")
        createdate = request.POST.get("createdate")
        #load all the rates
        rate = Croprate.objects.all()
        total = (int(tomatoes)*rate.tomatoe_rate + int(bell_pepper)*rate.bellpepper_rate + int(abernero)*rate.abernero_rate + int(cucumber)*rate.cucumber.rate)
        Invoice

        return render(request,'index.html')






