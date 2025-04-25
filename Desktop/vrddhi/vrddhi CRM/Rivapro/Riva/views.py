import json
import shutil
from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponse
from .models import ConfirmedOrderFollowUp, Enquiry, FollowUp_History,Products,Executive,FileUploadModel, Retail_FollowUp_History, inscategory, insurancecomp, motorncb, motorpolcoverage, motorpoltype, personal_Accident, personal_accident_FollowUp, policycopy, quotation, ConfirmedOrder,FollowUp, rccopymodel, retailpolicies, retailpolicies_FollowUp, suminstype
from .forms import ConfirmedOrderForm
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404
from django.core .paginator import Paginator
from django.db.models import Q,ForeignKey
import csv
import xlwt
import openpyxl
from django.template.loader import render_to_string
from xhtml2pdf import pisa

from reportlab.pdfgen import canvas
from io import BytesIO

# Create your views here.
def Home(request):
    current_user = request.user


    

    return render(request, 'xp/Home.html')


def enq_home(request):
    current_user = request.user
    selected_user_id = request.GET.get('user')
    selected_user = None

    if selected_user_id:
        selected_user = User.objects.filter(id=selected_user_id).first()
        # Managers/superusers see all enquiries (non-confirmed, non-lost, or reverted)
        enquiries = Enquiry.objects.filter(
            Q(is_confirmed=False, is_lost=False) 
        )
    else:
        # Other users see their own created or assigned enquiries (non-confirmed, non-lost, or reverted)
        enquiries = Enquiry.objects.filter(
            Q(is_confirmed=False, is_lost=False) 
        ).filter(
            Q(created_by=current_user) | Q(executive__name=current_user.username)
        )

    # Global search functionality
    search_query = request.GET.get('search', '')

    if search_query:
        global_filter = Q()

        for field in Enquiry._meta.fields:
            field_name = field.name

            if isinstance(field, ForeignKey):
                related_model = field.related_model
                related_fields = [f.name for f in related_model._meta.fields if f.name != 'id']
                for related_field in related_fields:
                    global_filter |= Q(**{f"{field_name}__{related_field}__icontains": search_query})

            elif field.choices:
                for value, display in dict(field.choices).items():
                    if search_query.lower() in display.lower():
                        global_filter |= Q(**{f"{field_name}": value})

            else:
                global_filter |= Q(**{f"{field_name}__icontains": search_query})

        # Apply the global filter
        enquiries = enquiries.filter(global_filter).order_by('-id')
    else:
        enquiries = enquiries.order_by('-id')

    # Pagination setup
    paginator = Paginator(enquiries, 10)  # 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Add a sequence number for display in the template
    start_sequence_number = (page_obj.number - 1) * paginator.per_page + 1
    for index, enquiry in enumerate(page_obj, start=start_sequence_number):
        enquiry.sequence_number = index

    # Render the response
    return render(request, 'xp/enqhome.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })



   

def enquiry_view(request):
    executive=Executive.objects.all()
    products=Products.objects.all()
    return render(request, 'xp/newenquiry.html',{'products':products , 'executive':executive})

def add_data(request):
    if request.method == "POST":
        # Retrieve form data
        company_name = request.POST.get("companyname")
        customer_name = request.POST.get("customername")
        reference_name = request.POST.get("refrencename")
        email = request.POST.get("email")
        contact = request.POST.get("contact")
        location = request.POST.get("location")
        status = request.POST.get("status")
        product_id = request.POST.get("products")
        subproduct = request.POST.get("subproduct")
        closure_date = request.POST.get("closuredate")
        executive_id = request.POST.get("executive_name")
        remarks = request.POST.get("remarks")

        files = request.FILES.getlist("attachment[]")

        # Validate and fetch related objects
        try:
            executive = Executive.objects.get(id=executive_id)
        except Executive.DoesNotExist:
            return HttpResponse("Invalid Executive selected", status=400)

        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            return HttpResponse("Invalid Product selected", status=400)

        # Create and save the enquiry record
        enquiry = Enquiry.objects.create(
            companyname=company_name,
            customername=customer_name,

            refrence=reference_name,
            email=email,
            contact=contact,
            location=location,
            status=status,
            products=product,
            subproduct=subproduct,
            closuredate=closure_date,
            executive=executive,
            remarks=remarks,
            created_by=request.user,  # Associate with the logged-in user
        )

        for file in files:
            file_upload = FileUploadModel.objects.create(file=file, name=file.name)
            enquiry.files.add(file_upload)

        enquiry.save()

        # Add visibility for both the logged-in user and selected executive
        enquiry.created_by = request.user  # Ensure the logged-in user is saved as creator
        enquiry.executive = executive  # Ensure the selected executive is assigned
        enquiry.save()

        return redirect("enquries")  # Redirect to enqhome page

    return HttpResponse("Invalid request method", status=405)




def enquiry_details(request, id):
    try:
        # Fetch the enquiry object by id
        enquiry = get_object_or_404(Enquiry, id=id)

        # Fetch only the revert remarks related to this enquiry
        revert_remarks = RevertRemark.objects.filter(enquiry=enquiry).order_by('-created_at')
        # Fetch the follow-ups related to this enquiry
        followupss = FollowUp.objects.filter(enquiry=enquiry).order_by('-fodate', '-fotime')

        # Files associated with the enquiry
        files = enquiry.files.all()

        # Data to pass to the template
        data = {
            "id": id,
            "companyname": enquiry.companyname,
            "customername": enquiry.customername,
            "refrence": enquiry.refrence,
            "email": enquiry.email,
            "contact": enquiry.contact,
            "location": enquiry.location,
            "status": enquiry.get_status_display() if enquiry.status else "N/A",
            "products": enquiry.products.name if enquiry.products else "N/A",  # Access the product name here
            "subproduct": enquiry.subproduct,
            "closuredate": enquiry.closuredate,
            "executive": enquiry.executive.name if enquiry.executive else "N/A",  # Similarly for executive name
            "remarks": enquiry.remarks,
            "files": files,
            "is_lost": "Lost" if enquiry.is_lost else "Active",
            'followups': followupss,  # Pass revert remarks here
        }

        # Handle POST request to add a follow-up
        if request.method == "POST":
            foname = request.POST.get('foname')
            fodate = request.POST.get('fodate')
            fotime = request.POST.get('fotime')

            # Save the follow-up record
            FollowUp.objects.create(
                enquiry=enquiry,
                foname=foname,
                fodate=fodate,
                fotime=fotime
            )

            # Redirect to the same page to display the updated follow-ups
            return redirect('enquiry_details', id=id)

        return render(request, 'xp/enquiry_details.html', {'enquiry_data': data ,'followupss': followupss, 'revert_remarks': revert_remarks,})

    except Enquiry.DoesNotExist:
        return HttpResponse("Enquiry not found", status=404)



from .forms import EnquiryForm

def edit_enquiry(request, enquiry_id): 
    enquiry = get_object_or_404(Enquiry, id=enquiry_id)
    
    if request.method == "POST":
        form = EnquiryForm(request.POST, request.FILES, instance=enquiry)

        if form.is_valid():
            # Access the 'products' field from form.cleaned_data after validation
            products = form.cleaned_data.get('products')  
            print(f"Products: {products}")

            # Save the changes to the database
            form.save()

            # Handle file uploads (if any)
            files = request.FILES.getlist("attachment[]")  # Get files from the request
            for file in files:
                # Create a FileUploadModel instance for each uploaded file
                file_upload = FileUploadModel.objects.create(file=file, name=file.name)
                enquiry.files.add(file_upload)  # Add the file to the Many-to-Many relationship

            # Save the enquiry after adding the files
            enquiry.save()

            # Display a success message and redirect
            messages.success(request, "Enquiry updated successfully!")
            return redirect('enquiry_details',enquiry_id)  # Redirect to enquiry homepage
        else:
            # Display error message if form is invalid
            messages.error(request, "There was an error updating the enquiry. Please fix the errors below.")
            print(form.errors)  # Log the errors for debugging
    else:
        # Display the form for GET request
        form = EnquiryForm(instance=enquiry)

    return render(request, 'xp/edit_enquiry.html', {'form': form, 'enquiry_id': enquiry_id})




from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Enquiry

from django.db.models import Q

def lost_orders_view(request):
    current_user = request.user
    selected_user_id = request.GET.get('user')
    selected_user = None

    # Admin users can view all users and filter by selected user
    users = User.objects.all()
    if selected_user_id:
        selected_user = User.objects.filter(id=selected_user_id).first()

    # Search functionality
    search_query = request.GET.get('search', '')
    global_filter = Q()

    # Define the fields you want to search
    searchable_fields = [
        'companyname',
        'customername',
        'contact',
        'remarks',
        'products__name',
        'closuredate',
    ]

    # Loop through each field and apply the search filter
    if search_query:
        for field in searchable_fields:
            global_filter |= Q(**{f"{field}__icontains": search_query})

    # Determine the queryset based on user type
    if current_user.is_superuser:
        # Superusers can view all lost enquiries and relegated confirmed_enquiry records
        lost_enquiries = Enquiry.objects.filter(is_lost=True).filter(global_filter)
        relegated_enquiries = Enquiry.objects.filter(is_relegated=True).filter(global_filter)
    else:
        # Non-superusers can only view their own lost or relegated enquiries
        lost_enquiries = Enquiry.objects.filter(is_lost=True, created_by=current_user).filter(global_filter)
        relegated_enquiries = Enquiry.objects.filter(
            is_relegated=True,
            created_by=current_user
        ).filter(global_filter)

    # Combine the two querysets using `union`
    combined_enquiries = lost_enquiries.union(relegated_enquiries)
    renewal = confirmed_enquiry.objects.filter(relegate=True)
    print(f"renewal",renewal)
    # Return the response with the filtered lost and relegated enquiries
    return render(request, 'xp/lost_orders.html', {
        'lost_enquiries': combined_enquiries,
        'renewal':renewal,
        'search_query': search_query,
        'users': users,
        'selected_user': selected_user,
    })

 
   


from django.shortcuts import get_object_or_404, redirect
from .models import Enquiry
from django.contrib import messages 

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from datetime import date, datetime, timezone

from datetime import datetime
from datetime import datetime
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Enquiry

def push_to_lost_order(request, id):
    if request.method == "POST":
        # Get the enquiry object
        enquiry = get_object_or_404(Enquiry, id=id)

        # Retrieve form data
        reason = request.POST.get('reason')
        lostdate = request.POST.get('lostdate')
        lost_renewal_days = request.POST.get('lost_renewal_days')

        # Parse the lostdate (if provided) into a datetime.date object
        try:
            if lostdate:
                lostdate = datetime.strptime(lostdate, "%Y-%m-%d").date()  # Parse to date
            else:
                lostdate = None  # Handle empty date gracefully
        except ValueError:
            messages.error(request, "Invalid date format for the lost date.")
            return redirect('enquiry_details', id=id)

        # Handle lost_renewal_days: Ensure it gets set to a valid number
        if lost_renewal_days:
            if lost_renewal_days.isdigit():
                lost_renewal_days = int(lost_renewal_days)  # Convert to int if valid
            else:
                messages.error(request, "Invalid value for lost renewal days.")
                return redirect('enquiry_details', id=id)
        else:
            lost_renewal_days = enquiry.lost_renewal_days  # Use default from model (30)

        # Update the enquiry fields
        enquiry.is_lost = True  # Mark as lost
        enquiry.flag = reason  # Save the reason
        enquiry.lostdate = lostdate  # Save the parsed date
        enquiry.lost_renewal_days = lost_renewal_days  # Save renewal days (ensure it's valid)

        # Save the enquiry with updated fields
        enquiry.save()

        # Display a success message
        messages.success(request, "Enquiry successfully moved to Lost Orders.")
        return redirect('lost_orders')  # Redirect to the Lost Orders page

    # If not POST, redirect to the enquiry details page
    messages.error(request, "Invalid request.")
    return redirect('enquiry_details', id=id)






def delete_lost_order(request, id):
    enquiry = get_object_or_404(Enquiry, id=id)
    enquiry.delete()

    messages.success(request, "Lost order deleted successfully.")
    return redirect('lost_orders')


def retrieve_lost_order(request, id):
    # Fetch the Enquiry object or return 404 if not found
    enquiry = get_object_or_404(Enquiry, id=id)

    # Check if the enquiry is relegated
    if enquiry.is_relegated:
        enquiry.is_reverted = True  # Mark as reverted
        enquiry.is_relegated = False  # Unmark as relegated

    # Always unmark as lost
    enquiry.is_lost = False  # Mark as active
    enquiry.save()  # Save the changes

    # Display success message
    messages.success(request, "Enquiry successfully retrieved from Lost Orders.")
    return redirect('enquiry_details')  # Redirect to the enquiries page


from collections import defaultdict

import json
import os
from collections import defaultdict
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from .models import Enquiry
import os
import json
from collections import defaultdict
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from .models import Enquiry






import os



from .models import confirmed_enquiry


from django.db.models import Max

from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Enquiry, confirmed_enquiry
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


def confirmed_orders(request):
    current_user = request.user
    selected_user_id = request.GET.get('user')
    selected_user = None

    if selected_user_id:
        selected_user = User.objects.filter(id=selected_user_id).first()

    # Check for expired confirmed_enquiry and set revert=True
    expired_enquiries = confirmed_enquiry.objects.filter(enddate__lt=now(), revert=False)
    expired_enquiries.update(revert=True)  # Mark expired entries as reverted

    # Filter confirmed orders excluding those with revert=True in confirmed_enquiry
    confirmed_orders = Enquiry.objects.filter(
        is_confirmed=True,
        created_by=current_user,
        confirmed_enquiry__revert=False  # Exclude reverted confirmed enquiries
    ).order_by('-id')

    search_query = request.GET.get('search', '')
    if search_query:
        global_filter = Q()
        searchable_fields = [
            'companyname',
            'customername',
            'contact',
            'products__name',
            'confirmed_enquiry__vid',
        ]
        for field in searchable_fields:
            global_filter |= Q(**{f"{field}__icontains": search_query})
        confirmed_orders = confirmed_orders.filter(global_filter)

    confirmed_orders = confirmed_orders.distinct()

    if 'revert' in request.GET:
        enquiry_id = request.GET.get('revert')
        enquiry = Enquiry.objects.filter(id=enquiry_id).first()
        if enquiry:
            enquiry.is_reverted = not enquiry.is_reverted if not enquiry.is_confirmed else False
            enquiry.save()
        return redirect('confirmedorderss')

    if 'push' in request.GET:
        enquiry_id = request.GET.get('push')
        enquiry = Enquiry.objects.filter(id=enquiry_id).first()
        if enquiry:
            enquiry.is_reverted = False
            enquiry.save()
        return redirect('confirmedorderss')

    if request.method == "POST":
        start_date = request.POST.get('startdate')
        end_date = request.POST.get('enddate')
        flag = request.POST.get('flag')
        policy_type = request.POST.get('policyType')
        renewal_days = request.POST.get('renewal_days')
        sum_am = request.POST.get('sum_insured')
        premium = request.POST.get('premium_amount')
        total = request.POST.get('GST_amount')
        calculated_gst = request.POST.get('calculated_gst')
        

        files = request.FILES.getlist('file_attachment')
        cname = request.POST.get('client_name')
        cphone = request.POST.get('client_phone')
        cemail = request.POST.get('client_email')
        vname = request.POST.get('vrddhi_name')
        vphone = request.POST.get('vrddhi_phone')
        vemail = request.POST.get('vrddhi_email')
        tname = request.POST.get('tpa_name')
        tphone = request.POST.get('tpa_phone')
        temail = request.POST.get('tpa_email')

        enquiry_id = request.POST.get('enquiry_id')
        enquiry = Enquiry.objects.filter(id=enquiry_id).first()

        if enquiry:
            enquiry.is_confirmed = True
            enquiry.is_reverted = False
            enquiry.save()

            current_month_year = now().strftime("%Y-%m")
            max_vid = confirmed_enquiry.objects.filter(vid__startswith=f"VID-{current_month_year}").aggregate(Max('vid'))
            last_vid_number = int(max_vid['vid__max'][-3:]) if max_vid['vid__max'] else 0
            new_vid_number = last_vid_number + 1
            new_vid = f"VID-{current_month_year}{str(new_vid_number).zfill(3)}"

            confirmed_enquiry_instance = confirmed_enquiry(
                created_by=current_user,
                enquiry=enquiry,
                startdate=start_date,
                enddate=end_date,
                flag=flag,
                policy_type=policy_type,
                renewal_days=renewal_days,
                sum_amount=sum_am,
                premium_amount=premium,
                Gst_amount=total,
                cal_gst=calculated_gst,
                revert=False,  # Initially set to False
                relegate=False,
                vid=new_vid,
                client_name=cname,
                client_phone=cphone,
                client_email=cemail,
                tpa_name=tname,
                tpa_phone=tphone,
                tpa_email=temail,
                vrd_name=vname,
                vrd_phone=vphone,
                vrd_email=vemail,
            )
            confirmed_enquiry_instance.save()
            for file in files:
                file_upload = FileUploadModel.objects.create(file=file, name=file.name)
                confirmed_enquiry_instance.files.add(file_upload)

            return redirect('confirmedorderss')

    return render(request, 'xp/confirmed_orders.html', {
        'confirmed_orders': confirmed_orders,
        'search_query': search_query,
        'selected_user': selected_user,
    })





def add_followup(request, id):
    followups = FollowUp.objects.all()
    if request.method == "POST":
        enquiry = get_object_or_404(Enquiry, id=id)
        foname = request.POST.get('foname')
        fodate_str = request.POST.get('fodate')
        fotime_str = request.POST.get('fotime')
        
        # Ensure fodate is a valid datetime object
        try:
            fodate = datetime.strptime(fodate_str, '%Y-%m-%d')  # Adjust the format as per your needs
        except ValueError:

            return redirect('enquiry_details', id=id)

        # Ensure fotime is a valid time object
        try:
            fotime = datetime.strptime(fotime_str, '%H:%M').time()  # Adjust the format as per your needs
        except ValueError:

            return redirect('enquiry_details', id=id)

        if foname and fodate and fotime:
            FollowUp.objects.create(
                enquiry=enquiry,
                foname=foname,
                fodate=fodate,
                fotime=fotime,

                
            )


            return redirect('enquiry_details', id=id)


        return redirect('enquiry_details', id=id)
    
    return HttpResponse("Invalid request", status=400)


def push_to_lost_order_from_confirmed(request, enquiry_id, vid):
    # Fetch the confirmed_enquiry record based on the quotation number
    confirmed_order = confirmed_enquiry.objects.filter(vid=vid).first()

    if not confirmed_order:
        messages.error(request, "No confirmed order found with the given quotation number.")
        return redirect('confirmedorderss')  # Redirect back if no confirmed order found

    # Access the related Enquiry object via the ForeignKey
    enquiry = confirmed_order.enquiry  # Access the related Enquiry object

    # Get the reason for moving the order to Lost Orders
    reason = request.POST.get("reason", "").strip()

    if not reason:
        messages.error(request, "Please provide a reason for moving the order to Lost Orders.")
        return redirect('confirmedorderss')  # Redirect back if no reason is provided

    # Update the 'relegate' field for the specific confirmed_enquiry
    confirmed_order.relegate = True
    confirmed_order.save()  # Save the updated confirmed_enquiry record

    # Also update the 'is_relegated' field of the related Enquiry object
    if enquiry:
        enquiry.is_relegated = True
        enquiry.save()  # Save the updated Enquiry record

    # Add success message
    messages.success(request, f"Quotation {vid} successfully moved to Lost Orders and Enquiry relegated.")

    # Redirect to Lost Orders page
    return redirect('lost_orders')





from django.shortcuts import render, get_object_or_404, redirect
from .models import ConfirmedOrderFollowUp, confirmed_enquiry

def add_confirmed_order_followup(request, enquiry_id, quotation_no):
    # Fetch the confirmed order based on enquiry_id and quotation_no
    try:
        order = confirmed_enquiry.objects.get(enquiry_id=enquiry_id, quotation=quotation_no)
    except confirmed_enquiry.DoesNotExist:
        return render(request, 'xp/confirmed_view.html', {
            'error': f"No confirmed order found for enquiry ID {enquiry_id} and quotation {quotation_no}",
        })
    except confirmed_enquiry.MultipleObjectsReturned:
        return render(request, 'xp/confirmed_view.html', {
            'error': f"Multiple confirmed orders found for enquiry ID {enquiry_id} and quotation {quotation_no}",
        })

    if request.method == 'POST':
        # Get the form data from the request
        foname = request.POST.get('foname')
        fodate = request.POST.get('fodate')
        fotime = request.POST.get('fotime')

        # Create a new follow-up associated with the confirmed order
        ConfirmedOrderFollowUp.objects.create(
            confirmed_order=order,
            foname=foname,
            fodate=fodate,
            fotime=fotime
        )

        # Redirect to the same page to display updated follow-ups
        return redirect('confirmed_view',quotation_no=quotation_no)

    # Get all follow-ups for the current confirmed order
    followups = ConfirmedOrderFollowUp.objects.filter(confirmed_order=order)

    # Render the template with the confirmed order and its follow-ups
    return render(request, 'xp/confirmed_view.html', {
        'order': order,
        'followups': followups,
        'enquiry_id': enquiry_id,         
        'quotation_number': quotation_no,
    })


from django.db.models.functions import TruncMonth
from django.db.models import Count, Sum
from django.shortcuts import render
from .models import Enquiry, ConfirmedOrder
from app.models import Target ,UserProfile,User


def dashboard(request):
    current_user = request.user

    followups = FollowUp.objects.all().order_by('-fodate', '-fotime')
    
    # Get the selected user from the dropdown, default to logged-in user if no selection is made
    selected_user_id = request.POST.get('user') if request.method == 'POST' else request.GET.get('user', request.user.id)
    
    try:
        selected_user = User.objects.get(id=selected_user_id)
    except User.DoesNotExist:
        selected_user = request.user  # Default to logged-in user if the selected user doesn't exist
    
    userprofile = UserProfile.objects.filter(user=selected_user).first()
    target = userprofile.target if userprofile else None
    
    if not request.user.is_authenticated:
        return redirect('login')

    total_target = Target.objects.filter(userprofile=userprofile).first()

    total_enquiries = Enquiry.objects.filter(created_by=selected_user).count()
    lost_enquiries = Enquiry.objects.filter(created_by=selected_user, status='lost').count()
    active_enquiries = Enquiry.objects.filter(created_by=selected_user, status='active').count()
     # Filter only orders created by the current user
    confirmed_orders = Enquiry.objects.filter(is_confirmed=True, created_by=current_user).count()
    lost_orders = Enquiry.objects.filter(is_lost=True, created_by=current_user).count()
    total_quotes = quotation.objects.filter(created_by=selected_user).count()
    active_policies = Enquiry.objects.filter(
        is_confirmed=True,
        created_by=current_user,
        confirmed_enquiry__revert=False  # Exclude reverted confirmed enquiries
    ).count()

    total_revenue = quotation.objects.filter(created_by=selected_user).aggregate(total_revenue=Sum('finalamount'))['total_revenue'] or 0
    if isinstance(total_revenue, str):
        total_revenue = float(total_revenue) if total_revenue else 0

    if total_enquiries > 0:
        conversion_ratio = (active_policies / total_enquiries) * 100
    else:
        conversion_ratio = 0

    target_value = 0
    if total_target and total_target.value:
        try:
            target_value = float(total_target.value)
            if target_value > 0:
                target_ratio = (active_policies / target_value) * 100
            else:
                target_ratio = 0
        except ValueError:
            target_ratio = 0
    else:
        target_ratio = 0

    target_to_reach = max(0, int(target_value - active_policies))

    today = now().date()
    
     # Count of Confirmed Orders Due for Renewal
    confirmed_orders_due_for_renewal = []
    for confirmed_entry in confirmed_enquiry.objects.filter(created_by=selected_user):
        if not confirmed_entry.renewal_flag and not confirmed_entry.revert:
            renewal_date = confirmed_entry.enddate - timedelta(days=confirmed_entry.renewal_days)
            if now().date() >= renewal_date:
                confirmed_orders_due_for_renewal.append(confirmed_entry)

    # Count of Lost Orders Due for Renewal
    lost_orders_due_for_renewal = [
        order for order in Enquiry.objects.filter(created_by=selected_user, is_lost=True)
        if order.is_lost_for_renewal()
    ]

    # ✅ Total Renewals Count
    total_renewals = len(confirmed_orders_due_for_renewal) + len(lost_orders_due_for_renewal)

    monthly_data = (
        Enquiry.objects.filter(created_by=selected_user)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    labels = [data['month'].strftime('%B') for data in monthly_data]
    data = [data['count'] for data in monthly_data]

    users = User.objects.all()

    

    context = {
        'total_enquiries': total_enquiries,
        'total_renewals':total_renewals,
        'lost_enquiries': lost_enquiries,
        'active_enquiries': active_enquiries,
        'confirmed_orders': confirmed_orders,
        'active_policies':active_policies,
        'lost_orders': lost_orders,
        'conversion_ratio': conversion_ratio,
        'monthly_labels': labels,
        'monthly_data': data,
        'total_quotes': total_quotes,
        'total_revenue': total_revenue,
        'target': target,
        'target_ratio': target_ratio,
        'target_to_reach': target_to_reach,
        'users': users,
        'selected_user': selected_user,
        'followups': followups
    }

    return render(request, 'xp/dashboard.html', context)




from datetime import datetime
from django.shortcuts import render










from django.shortcuts import get_object_or_404, redirect, render
from .models import confirmed_enquiry,RevertRemark

from django.shortcuts import get_object_or_404, redirect
from django.utils.timezone import now
from django.contrib import messages

def revert_to_enquiries(request, enquiry_id):
    
    if request.method == "POST":
        
        # Get the remarks and timestamp from the form
        remarks = request.POST.get("remarks")
        timestamp = request.POST.get("timestamp") or now()  # Default to current timestamp

        # Get the enquiry object
        
        enquiry = get_object_or_404(Enquiry, Q(id=enquiry_id) & (Q(is_confirmed=True) | Q(is_lost=True)))
        
        # Create a new revert remark and save it
        RevertRemark.objects.create(
            enquiry=enquiry,
            text=remarks,
            created_at=timestamp
        )

        # Update the enquiry's status
        enquiry.is_reverted = True  # Mark as reverted
        
        enquiry.save()
        

        # Update the `revert` status for all related `confirmed_enquiry` entries
        confirmed_enquiries = confirmed_enquiry.objects.filter(enquiry=enquiry)
        confirmed_enquiries.update(revert=True)  # Update all related entries in bulk

        # Redirect to the enquiry details page with the enquiry ID
        messages.success(request, "Enquiry successfully reverted.")
        return redirect('enquiry_details', id=enquiry_id)

    # Redirect for non-POST requests
    return redirect('enquiry_details', id=enquiry_id)







from reportlab.lib.pagesizes import letter

from .views import RevertRemark

def export_pdf_details(request, enquiry_id):
    try:
        enquiry_data = get_object_or_404(Enquiry, id=enquiry_id)
        revert_remarks = enquiry_data.revert_remarks.all()  # Access related revert remarks
        followups = enquiry_data.followups.all()  # Access related follow-ups using the correct related_name
    except Enquiry.DoesNotExist:
        return HttpResponse("Enquiry not found.", status=404)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="enquiry_{enquiry_id}_details.pdf"'

    pdf_canvas = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    y = height - 50

    # Header
    pdf_canvas.setFont("Helvetica-Bold", 16)
    pdf_canvas.drawString(200, y, "Enquiry Details Report")
    y -= 40

    pdf_canvas.setFont("Helvetica", 12)

    # Enquiry Details
    details = [
        f"Company Name: {enquiry_data.companyname}",
        f"Customer Name: {enquiry_data.customername}",
        f"Reference: {enquiry_data.refrence}",
        f"Email: {enquiry_data.email}",
        f"Contact: {enquiry_data.contact}",
        f"Location: {enquiry_data.location}",
        f"Status: {enquiry_data.status}",
        f"Products: {enquiry_data.products}",
        f"Sub Product: {enquiry_data.subproduct}",
        f"Closure Date: {enquiry_data.closuredate}",
        f"Executive: {enquiry_data.executive}",
        f"Remarks: {enquiry_data.remarks}",
    ]
    for detail in details:
        if y < 50:
            pdf_canvas.showPage()
            y = height - 50
        pdf_canvas.drawString(50, y, detail)
        y -= 15

    # Revert Remarks
    if y < 70:
        pdf_canvas.showPage()
        y = height - 50
    pdf_canvas.setFont("Helvetica-Bold", 12)
    pdf_canvas.drawString(50, y, "Revert Remarks:")
    y -= 20

    pdf_canvas.setFont("Helvetica", 10)
    if revert_remarks.exists():
        for remark in revert_remarks:
            if y < 50:
                pdf_canvas.showPage()
                y = height - 50
            pdf_canvas.drawString(50, y, f"- {remark.text} ({remark.created_at})")
            y -= 15
    else:
        pdf_canvas.drawString(50, y, "No revert remarks available.")
        y -= 15

    # Follow-Ups
    if y < 70:
        pdf_canvas.showPage()
        y = height - 50
    pdf_canvas.setFont("Helvetica-Bold", 12)
    pdf_canvas.drawString(50, y, "Follow-Up History:")
    y -= 20

    pdf_canvas.setFont("Helvetica", 10)
    if followups.exists():
        for followup in followups:
            if y < 50:
                pdf_canvas.showPage()
                y = height - 50
            pdf_canvas.drawString(50, y, f"- Name: {followup.foname}, Date: {followup.fodate}, Time: {followup.fotime}")
            y -= 15
    else:
        pdf_canvas.drawString(50, y, "No follow-ups recorded.")
        y -= 15

    # Files
    if y < 70:
        pdf_canvas.showPage()
        y = height - 50
    pdf_canvas.setFont("Helvetica-Bold", 12)
    pdf_canvas.drawString(50, y, "Attached Files:")
    y -= 20

    pdf_canvas.setFont("Helvetica", 10)
    if enquiry_data.files.exists():
        for file in enquiry_data.files.all():
            if y < 50:
                pdf_canvas.showPage()
                y = height - 50
            pdf_canvas.drawString(50, y, f"- {file.name}: {file.file.url}")
            y -= 15
    else:
        pdf_canvas.drawString(50, y, "No files uploaded.")
        y -= 15

    # Save and return response
    pdf_canvas.showPage()
    pdf_canvas.save()

    return response



def export_confirmed_orders_pdf(request):
    # Get the search query from GET request
    search_query = request.GET.get('search', '')

    # Filter confirmed orders based on search query
    confirmed_orders = ConfirmedOrder.objects.all()
    if search_query:
        confirmed_orders = confirmed_orders.filter(companyname__icontains=search_query)  # Adjust filter as needed

    # Pagination logic (optional)
    paginator = Paginator(confirmed_orders, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Render the template with the filtered and paginated data
    html = render_to_string('xp/confirmed_orders_pdf_template.html', {'confirmed_orders': page_obj.object_list})

    # Create a PDF response using xhtml2pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="confirmed_orders.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response

from django.utils.timezone import now
from datetime import timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Enquiry, confirmed_enquiry, Notification

def Renewals(request):
    current_user = request.user
    selected_user_id = request.GET.get('user')
    selected_user = User.objects.filter(id=selected_user_id).first() if selected_user_id else None

    # Filter only orders created by the current user
    confirmed_orders = Enquiry.objects.filter(is_confirmed=True, created_by=current_user)
    lost_orders = Enquiry.objects.filter(is_lost=True, created_by=current_user)

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        global_filter = Q()
        for field in ['companyname', 'customername', 'contact', 'products__name', 'confirmed_enquiry__vid']:
            global_filter |= Q(**{f"{field}__icontains": search_query})
        confirmed_orders = confirmed_orders.filter(global_filter)
        lost_orders = lost_orders.filter(global_filter)

    confirmed_orders = confirmed_orders.distinct()
    lost_orders = lost_orders.distinct()

    # Today's date
    today = now().date()
    confirmed_orders_due_for_renewal = []

    # ✅ Iterate through confirmed orders and their confirmed_enquiry but exclude reverted ones
    for order in confirmed_orders:
        for confirmed_entry in order.confirmed_enquiry_set.filter(revert=False):  # Exclude reverted entries
            renewal_date = confirmed_entry.enddate - timedelta(days=confirmed_entry.renewal_days)
            if today >= renewal_date and not confirmed_entry.renewal_flag:
                confirmed_orders_due_for_renewal.append(confirmed_entry)

               

     # Handle lost orders due for renewal
    lost_orders_due_for_renewal = [order for order in lost_orders if order.is_lost_for_renewal()]

    # # ✅ Create notification for lost orders
    # for lost in lost_orders_due_for_renewal:
    #     Notification.objects.get_or_create(
    #         user=current_user,
    #         enquiry=lost,
    #         message=f"Lost{lost.id}renewal on {lost.lostdate}."
    #     )

    # Handle POST request for renewal submission
    if request.method == "POST":
        enquiry_id = request.POST.get('enquiry_id')
        remarks = request.POST.get('remarks')
        enquiry = get_object_or_404(Enquiry, id=enquiry_id)

        if enquiry.is_lost:
            enquiry.is_lost_renewed = True
            enquiry.remarks = remarks
            enquiry.save()
        else:
            confirmed_entry = confirmed_enquiry.objects.filter(enquiry=enquiry).first()
            if confirmed_entry:
                confirmed_entry.renewal_flag = True
                confirmed_entry.remarks = remarks
                confirmed_entry.save()

        # ✅ Delete the notification after renewal
        Notification.objects.filter(enquiry=enquiry).delete()
        return redirect('renewals')

    # Render the template
    return render(request, 'xp/renewals.html', {
        'confirmed_orders_due_for_renewal': confirmed_orders_due_for_renewal,
        'lost_orders_due_for_renewal': lost_orders_due_for_renewal,
        'search_query': search_query,
        'selected_user': selected_user,
    })



def Icrm(request):

    return render(request,'xp/Icrm.html')


################################################# icrm #################
from django.db.models import Q

def I_enq_home(request):
    current_user = request.user
    selected_user_id = request.GET.get('user')
    selected_user = None
    search_query = request.GET.get('search', '').strip()

    selected_user = User.objects.filter(id=selected_user_id).first()



   
    client_data=clients.objects.all().order_by('-id')
    motorpol_data=motorpol.objects.all().order_by('-id')

    # ✅ Update retailpolicies where enddate has passed, setting renewals=True
    expired_retail_policies = retailpolicies.objects.filter(enddate__lt=now(), renewals=False)
    expired_retail_policies.update(renewals=True)

    # ✅ Update personal_Accident where end_date has passed, setting renewals=True
    expired_personal_acc = personal_Accident.objects.filter(end_date__lt=now(), renewals=False)
    expired_personal_acc.update(renewals=True)

     # ✅ Exclude records from retailpolicies where renewals=True
    retailpolicies_data = retailpolicies.objects.filter(
        renewals=False
    ).order_by('-id')

    # ✅ Exclude records from personal_Accident where renewals=True
    personal_acc = personal_Accident.objects.filter(
        renewals=False
    ).order_by('-id')

    inscat=inscategory.objects.all().order_by('-id')
    # Apply search filter
    if search_query:
        cleaned_query = search_query.replace(" ", "").replace("-", "").replace("+", "")
        client_data = client_data.filter(
            Q(cname__icontains=search_query) |  
            Q(cemail__icontains=search_query) |
            Q(ccontact__icontains=cleaned_query)
        )

        retailpolicies_data = retailpolicies_data.filter(
            Q(id__icontains=search_query) |  # Search by Retail Policy ID
            Q(insbranch__insbranch__icontains=search_query) |  # Search by Insurance Branch Name
            Q(retpol__insname__icontains=search_query) |  # Search by Insurance Policy Name
            Q(inscomp__insname__icontains=search_query) |  # Search by Insurance Company Name
            Q(polno__icontains=search_query) |  # Search by Policy Number
            Q(cid__cname__icontains=search_query)  # Search by Client Name
        )
        personal_acc = personal_acc.filter(
            Q(id__icontains=search_query) |  
            Q(inscomp_name__insname__icontains=search_query) |  # Search by Insurance Company
            Q(ins_branch__insbranch__icontains=search_query) |  # Search by Branch
            Q(policy_no__icontains=search_query) |  # Search by Policy Number
            Q(contact_person__icontains=search_query) |  # Search by Contact Person Name
            Q(cid__cname__icontains=search_query) |  # Search by Client Name
            Q(aadhar__icontains=search_query) |  # Search by Aadhar Number
            Q(pan_card__icontains=search_query)  # Search by PAN Card Number
        )


    # Render the response
    return render(request, 'xp/i_enqhome.html', {
        # 'page_obj': page_obj,
        'search_query': search_query,
        'client_data':client_data,
        'motorpol_data':motorpol_data,
        'retailpolicies_data':retailpolicies_data,
        'inscat':inscat,
        'personal_acc':personal_acc,

    })


def I_Renewals(request):
    current_user = request.user
    selected_user_id = request.GET.get('user')
    selected_user = None
    search_query = request.GET.get('search', '').strip()  # Get search query

    if selected_user_id:
        selected_user = User.objects.filter(id=selected_user_id).first()

    # Calculate the date 30 days from now
    today = now().date()  # Current date
    renewal_date = today + timedelta(days=30)

     # ✅ Exclude records with renewals=True and filter records with enddate within 30 days
    renewal_policies = retailpolicies.objects.filter(
        enddate__lte=renewal_date,
        enddate__gte=today,
        renewals=False  # ✅ Exclude records where renewals=True
    ).order_by('-id')

    # ✅ Exclude records with renewals=True and filter records with end_date within 30 days
    personal_acc = personal_Accident.objects.filter(
        end_date__lte=renewal_date,
        end_date__gte=today,
        renewals=False  # ✅ Exclude records where renewals=True
    ).order_by('-id')
    print(personal_acc)
    

    # Apply search filter across multiple fields
    if search_query:
        renewal_policies = renewal_policies.filter(
            Q(cid__cname__icontains=search_query) |  # Client Name
            Q(polno__icontains=search_query) |  # Policy No
            Q(retpol__insname__icontains=search_query) |  # Category Name (inscategory)
            Q(inscomp__insname__icontains=search_query) |  # Insurer Name (insurancecomp)
            Q(insbranch__insbranch__icontains=search_query) |  # Branch Name (insurancebranch)
            Q(insbranch__branch_pincode__icontains=search_query) |  # Branch Pincode
            Q(strtdate__icontains=search_query) |  # Start Date
            Q(enddate__icontains=search_query) |  # End Date
            Q(cid__ccontact__icontains=search_query)  # Contact Number
        )

        personal_acc = personal_acc.filter(
            Q(cid__cname__icontains=search_query) |  # Client Name
            Q(policy_no__icontains=search_query) |  # Policy No
            Q(category__insname__icontains=search_query) |  # Category Name (inscategory)
            Q(inscomp_name__insname__icontains=search_query) |  # Insurer Name (insurancecomp)
            Q(ins_branch__insbranch__icontains=search_query) |  # Branch Name (insurancebranch)
            Q(ins_branch__branch_pincode__icontains=search_query) |  # Branch Pincode
            Q(start_date__icontains=search_query) |  # Start Date
            Q(end_date__icontains=search_query) |  # End Date
            Q(cid__ccontact__icontains=search_query)  # Contact Number
        )



    #  # Create notifications if they don’t already exist
    # for policy in renewal_policies:
    #     print("i renewals 1")
    #     Notification.objects.get_or_create(
    #         user=current_user,
    #         retail=policy,
    #         policy_no=policy.polno,
    #         message=f" {policy.polno} renewal on {policy.enddate}.",
    #     )
    #     # **Remove notification if 'revert' is True**
    #     if policy.renewals:
    #         Notification.objects.filter( policy_no=policy.polno).delete()

    # for policy in personal_acc:
    #     print("i renewals 2")
    #     Notification.objects.get_or_create(
    #         user=current_user,
    #         personal=policy,
    #         policy_no=policy.policy_no,
    #         message=f" {policy.policy_no} renewal on {policy.end_date}.",
    #     )
    #      # **Remove notification if 'revert' is True**
    #     if policy.renewals:
    #         Notification.objects.filter( policy_no=policy.policy_no).delete()
    

    return render(request, 'xp/i_renewals.html', {
        'renewal_policies': renewal_policies,
        'personal_acc':personal_acc,
        'search_query':search_query,
        'selected_user': selected_user,
    })


from datetime import datetime, timedelta
from django.shortcuts import render
from django.utils.timezone import now
from .models import retailpolicies  

def Renewal_filter_policies(request):
    today = now().date()  
    renewal_date = today + timedelta(days=30)

    # Default: Show policies expiring in the next 30 days
    policies = retailpolicies.objects.filter(enddate__lte=renewal_date, enddate__gte=today).order_by('-id')

    # Get start and end dates from request (MATCHING FORM FIELD NAMES)
    start_date = request.GET.get('start-date')  
    end_date = request.GET.get('end-date')

    print(f"Start Date: {start_date}, End Date: {end_date}")  # Debugging

    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

            policies = retailpolicies.objects.filter(enddate__gte=start_date, enddate__lte=end_date).order_by('-id')
        except ValueError:
            print("Invalid date format")  

    print(f"Filtered Policies: {policies}")  

    context = {
        'renewal_policies': policies,
        'start_date': start_date if 'start_date' in locals() else '',
        'end_date': end_date if 'end_date' in locals() else '',
    }
    
    return render(request, 'xp/i_renewals.html', context)






from itertools import chain

from django.db.models import Sum
def I_dashboard(request):
    followups = FollowUp.objects.all().order_by('-fodate', '-fotime')
    
    # Get the selected user from the dropdown, default to logged-in user if no selection is made
    selected_user_id = request.POST.get('user') if request.method == 'POST' else request.GET.get('user', request.user.id)
    
    try:
        selected_user = User.objects.get(id=selected_user_id)
    except User.DoesNotExist:
        selected_user = request.user  # Default to logged-in user if the selected user doesn't exist
    
    userprofile = UserProfile.objects.filter(user=selected_user).first()
    target = userprofile.target if userprofile else None
    
    if not request.user.is_authenticated:
        return redirect('login')

    total_target = Target.objects.filter(userprofile=userprofile).first()

    total_enquiries = Enquiry.objects.filter(created_by=selected_user).count()
    lost_enquiries = Enquiry.objects.filter(created_by=selected_user, status='lost').count()
    active_enquiries = Enquiry.objects.filter(created_by=selected_user, status='active').count()
    confirmed_orders = ConfirmedOrder.objects.filter(created_by=selected_user).count()
    lost_orders = Enquiry.objects.filter(created_by=selected_user, is_lost=True).count()
    total_quotes = quotation.objects.filter(created_by=selected_user).count()
    client_data=clients.objects.all().order_by('-id').count()
    total_premium = personal_Accident.objects.aggregate(total=Sum('premium'))['total'] or 0


    # Calculate the date 30 days from now
    today = now().date()  # Current date
    renewal_date = today + timedelta(days=30)


    renewal_policies = retailpolicies.objects.filter(
        enddate__lte=renewal_date,
        enddate__gte=today,
        renewals=False  # ✅ Exclude records where renewals=True
    ).order_by('-id')

    # ✅ Exclude records with renewals=True and filter records with end_date within 30 days
    personal_acc = personal_Accident.objects.filter(
        end_date__lte=renewal_date,
        end_date__gte=today,
        renewals=False  # ✅ Exclude records where renewals=True
    ).order_by('-id')
    print(personal_acc)

    total_renewals = list(chain(renewal_policies, personal_acc))
    total_count=len(total_renewals)
    print(total_count)


     # ✅ Exclude records from retailpolicies where renewals=True
    retailpolicies_data = retailpolicies.objects.filter(
        renewals=False
    ).order_by('-id')

    # ✅ Exclude records from personal_Accident where renewals=True
    personal_acc_data = personal_Accident.objects.filter(
        renewals=False
    ).order_by('-id')

    active_policy=list(chain(personal_acc_data,retailpolicies_data))
    policy_count=len(active_policy)

    total_revenue = quotation.objects.filter(created_by=selected_user).aggregate(total_revenue=Sum('finalamount'))['total_revenue'] or 0
    if isinstance(total_revenue, str):
        total_revenue = float(total_revenue) if total_revenue else 0

    if total_enquiries > 0:
        conversion_ratio = (confirmed_orders / total_enquiries) * 100
    else:
        conversion_ratio = 0

    target_value = 0
    if total_target and total_target.value:
        try:
            target_value = float(total_target.value)
            if target_value > 0:
                target_ratio = (confirmed_orders / target_value) * 100
            else:
                target_ratio = 0
        except ValueError:
            target_ratio = 0
    else:
        target_ratio = 0

    target_to_reach = max(0, int(target_value - confirmed_orders))

    monthly_data = (
        Enquiry.objects.filter(created_by=selected_user)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    labels = [data['month'].strftime('%B') for data in monthly_data]
    data = [data['count'] for data in monthly_data]

    users = User.objects.all()

    context = {
        'total_enquiries': total_enquiries,
        'total_premium':total_premium,
        'lost_enquiries': lost_enquiries,
        'active_enquiries': active_enquiries,
        'confirmed_orders': confirmed_orders,
        'lost_orders': lost_orders,
        'conversion_ratio': conversion_ratio,
        'total_renewals':total_renewals,
        'policy_count':policy_count,
        'total_count':total_count,
        'monthly_labels': labels,
        'monthly_data': data,
        'total_quotes': total_quotes,
        'total_revenue': total_revenue,
        'target': target,
        'target_ratio': target_ratio,
        'target_to_reach': target_to_reach,
        'users': users,
        'selected_user': selected_user,
        'client_data':client_data,
        'followups': followups
    }

    return render(request, 'xp/i_dashboard.html', context)



def Past_policies(request):
    # Get all confirmed enquiries where revert is True
    past_policies = confirmed_enquiry.objects.filter(revert=True)

    # Handle search if needed
    search_query = request.GET.get('search', '')
    if search_query:
        global_filter = Q()
        searchable_fields = [
            'enquiry__companyname',
            'enquiry__customername',
            'enquiry__contact',
            'startdate',
            'enddate',
            'policy_type',
            'vid',
        ]
        for field in searchable_fields:
            global_filter |= Q(**{f"{field}__icontains": search_query})
        past_policies = past_policies.filter(global_filter)

    past_policies = past_policies.distinct()

    return render(request, 'xp/past_policy.html', {
        'past_policies': past_policies,
        'search_query': search_query,
    })


# def I_add_enquiry(request):
#     current_user = request.user

#     return render(request,'xp/i_new_enquiry.html')
from datetime import datetime

def I_add_enquiry(request):
    inscat=inscategory.objects.all()
    polty=motorpoltype.objects.all()
    mtrpolcov=motorpolcoverage.objects.all()
    mtncb=motorncb.objects.all() 
    insurer=insurancecomp.objects.all()
    sumtype=suminstype.objects.all()
    ibranch=insurancebranch.objects.all()
    renewals=retailpolicies.objects.filter(uid=User.objects.get(id=request.user.id),enddate__gte=date.today()).all().order_by('-enddate')    
    rncount=0
    # for r in renewals:
    #     if (r.enddate-today).days < 46:
    #         rncount=rncount+1 
    return render(request, 'xp/i_new_enquiry.html',{"inscat":inscat,"poltyp":polty,'mtrpolcov':mtrpolcov,'mtrncb':mtncb,'insurer':insurer,'sumtype':sumtype,"rncount":rncount,'ibranch':ibranch,'renewals':renewals})

from django.shortcuts import redirect
from django.http import HttpResponse
from .models import clients, motorpol, retailpolicies, motorncb, motorpolcoverage, motorpoltype, insurancecomp, insurancebranch, inscategory
from django.contrib.auth.models import User

from django.http import JsonResponse
from django.shortcuts import redirect
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import transaction

def i_submit_form_vehicle(request):
    if request.method == 'POST':
        try:
            # Debugging output for POST data
            for key, value in request.POST.items():
                print(f'{key}: {value}')

            # Collect data for `clients`
            cname = request.POST.get('field1_cname')
            caddress = request.POST.get('field1_caddress')
            ccontact = request.POST.get('field1_ccontact')
            cemail = request.POST.get('field1_cemail')

            # Collect data for `motorpol`
            expolno = request.POST.get('field2_expolno')
            engineno = request.POST.get('field2_engineno')
            chassisno = request.POST.get('field2_chassisno')
            dor = request.POST.get('field2_dor')  # Ensure this is not empty
            ncb_id = request.POST.get('field2_ncb')
            regno = request.POST.get('field2_regno')
            rtocity = request.POST.get('field2_rtocity')
            polcov_id = request.POST.get('field2_polcov')
            poltype_id = request.POST.get('field2_poltype')
            rccopy_files = request.FILES.getlist("attachment[]")  # Multiple files
            tpname_id = request.POST.get('field2_tpname')
            makemodel = request.POST.get('field2_makemodel')
            idv = request.POST.get('field2_idv')

            if not dor:
                return JsonResponse({'error': 'The "Date of Registration" (dor) field is required.'}, status=400)

            # Collect data for `retailpolicies`
            uid_id = request.user.id  # Foreign Key
            inscomp_id = request.POST.get('field3_inscomp')
            category = request.POST.get('field3_category')
            insbranch_id = request.POST.get('field3_insbranch')
            strtdate = request.POST.get('field3_strtdate')
            enddate = request.POST.get('field3_enddate')
            amtpd = request.POST.get('field3_amtpd')
            amt_gst = request.POST.get('field3_gst_value')
            sum_insured = request.POST.get('field3_amt_insured')
            amtpdgst = request.POST.get('field3_amtpdgst')
            polno = request.POST.get('field3_polno')
            newpolcopy = request.FILES.getlist("policy_attachment[]")   # Handle file upload

            # Start transaction
            with transaction.atomic():
                # Save `clients`
                client = clients.objects.create(
                    cname=cname or "Unknown",  # Provide a default if cname is empty
                    caddress=caddress or "",   # Allow empty strings
                    ccontact=ccontact or None,  # Use None for optional fields
                    cemail=cemail or None,
                )

                # Save `motorpol`
                motor = motorpol.objects.create(
                    cid=client,
                    expolno=expolno or None,
                    engineno=engineno or None,
                    chassisno=chassisno or None,
                    dor=dor or None,  # Make sure this field allows null in the model
                    ncb_id=ncb_id or None,
                    regno=regno or None,
                    rtocity=rtocity or None,
                    polcov_id=polcov_id or None,
                    poltype_id=poltype_id or None,
                    tpname_id=tpname_id or None,
                    makemodel=makemodel or None,
                    idv=idv or 0,  # Set a default numerical value
                )

                # Save RC Copy files
                for file in rccopy_files:
                    file_upload = rccopymodel.objects.create(file=file)
                    motor.rccopy.add(file_upload)  # Add each file to the ManyToManyField

                # Save `retailpolicies`
                retail = retailpolicies.objects.create(
                    uid_id=uid_id,
                    cid=client,
                    inscomp_id=inscomp_id or None,
                    retpol=inscategory.objects.get(pk=category) if category else None,
                    insbranch_id=insbranch_id or None,
                    strtdate=strtdate or None,
                    enddate=enddate or None,
                    amtpd=amtpd or 0,  # Default numeric fields to 0
                    amtpdgst=amtpdgst or 0,
                    gstval=amt_gst or 0,
                    amount_insured=sum_insured or 0,
                    polno=polno or None,
                )

                # Save RC Copy files
                for file in newpolcopy:
                    file_upload = policycopy.objects.create(file=file)
                    retail.newpolcopy.add(file_upload) 
            return redirect('ienquiry')

        except Exception as e:
            print(f'Error occurred: {e}')
            return JsonResponse({'error': 'An error occurred while processing the form. Please try again.'}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def policy_details(request, id):
    
    policy = get_object_or_404(retailpolicies, id=id)
    motor = motorpol.objects.filter(cid=policy.cid).first()    
    rccopy = motor.rccopy.all()
    pcopy=policy.newpolcopy.all()
    retailfollowups=retailpolicies_FollowUp.objects.filter(retail=id)   
    # print(retailfollowups)

    data={
        "id":id,
        "cid":policy.cid,
        "retpol":policy.retpol,
        "inscomp":policy.inscomp,
        "insbranch":policy.insbranch,
        "strtdate":policy.strtdate,
        "enddate":policy.enddate,
        "amtpd":policy.amtpd,
        "amtpdgst":policy.amtpdgst,
        "polno":policy.polno,
        "newpolcopy":policy.newpolcopy,
        "gstval":policy.gstval,
        "amount_insured":policy.amount_insured,
    }

    return render(request,'xp/policy_details.html',{'policy':data,'motor':motor,'rccopy': rccopy,'pcopy':pcopy,'retailfollowups':retailfollowups})



def I_add_renewal(request, cid):

    inscat = inscategory.objects.all()
    polty = motorpoltype.objects.all()
    mtrpolcov = motorpolcoverage.objects.all()
    mtncb = motorncb.objects.all()
    insurer = insurancecomp.objects.all()
    sumtype = suminstype.objects.all()
    ibranch = insurancebranch.objects.all()
 
    # Retrieve the selected retail policy
    policy = retailpolicies.objects.get(id=cid)
    policy.renewals=True
    policy.save()

    nwp=retailpolicies.objects.get(id=cid)
    motor=motorpol.objects.get(cid=nwp.cid)

    renewals = retailpolicies.objects.filter(
        uid=User.objects.get(id=request.user.id),
        enddate__gte=date.today()
    ).all().order_by('-enddate')

     # Prepopulate the form with the selected policy's details
    form_data = {
        "field1_cname": policy.cid.cname,
        "field1_ccontact": policy.cid.ccontact,
        "field1_cemail": policy.cid.cemail,
        "field1_caddress": policy.cid.caddress,
        "field2_expolno": policy.polno,
        "field2_makemodel":motor.makemodel,
        "field2_engineno":motor.engineno,
        "field2_chassisno":motor.chassisno,
        "field2_regno":motor.regno,
        "field2_rtocity":motor.rtocity,

    }


    return render(request, 'xp/i_new_enquiry.html', {
        "inscat": inscat,
        "poltyp": polty,
        "mtrpolcov": mtrpolcov,
        "mtrncb": mtncb,
        "insurer": insurer,
        "sumtype": sumtype,
        "ibranch": ibranch,
        "renewals": renewals,
        "policy": policy,
        "motor":motor,
        "form_data":form_data,  
    })


def retail_Past_policy(request):
    # Get all confirmed enquiries where revert is True
    past_policies = retailpolicies.objects.filter(renewals=True).order_by('-id')
    personal=personal_Accident.objects.filter(renewals=True).order_by('-id')
    search_query = request.GET.get('search', '').strip()



    # Apply search filter if a query is provided
    if search_query:
        past_policies = past_policies.filter(
            Q(cid__cname__icontains=search_query) |  # Client Name
            Q(polno__icontains=search_query) |  # Policy No
            Q(retpol__insname__icontains=search_query) |  # Category Name (inscategory)
            Q(inscomp__insname__icontains=search_query) |  # Insurer Name (insurancecomp)
            Q(insbranch__insbranch__icontains=search_query) |  # Branch Name (insurancebranch)
            Q(insbranch__branch_pincode__icontains=search_query) |  # Branch Pincode
            Q(strtdate__icontains=search_query) |  # Start Date
            Q(enddate__icontains=search_query) |  # End Date
            Q(cid__ccontact__icontains=search_query)  # Contact Number
        )

        personal = personal.filter(
            Q(cid__cname__icontains=search_query) |  # Client Name
            Q(policy_no__icontains=search_query) |  # Policy No
            Q(category__insname__icontains=search_query) |  # Category Name (inscategory)
            Q(inscomp_name__insname__icontains=search_query) |  # Insurer Name (insurancecomp)
            Q(ins_branch__insbranch__icontains=search_query) |  # Branch Name (insurancebranch)
            Q(ins_branch__branch_pincode__icontains=search_query) |  # Branch Pincode
            Q(start_date__icontains=search_query) |  # Start Date
            Q(end_date__icontains=search_query) |  # End Date
            Q(cid__ccontact__icontains=search_query)  # Contact Number
        )

    return render(request, 'xp/retail_past_policy.html', {
        'past_policies': past_policies,
        'personals': personal,
        'search_query':search_query,

    })



def retail_policy_add_followup(request, id):
    retailfollowups = retailpolicies_FollowUp.objects.all()
    if request.method == "POST":
        retail = get_object_or_404(retailpolicies, id=id)
        foname = request.POST.get('foname')
        fodate_str = request.POST.get('fodate')
        fotime_str = request.POST.get('fotime')
        
        # Ensure fodate is a valid datetime object
        try:
            fodate = datetime.strptime(fodate_str, '%Y-%m-%d')  # Adjust the format as per your needs
        except ValueError:

            return redirect('i_policy_details', id=id)

        # Ensure fotime is a valid time object
        try:
            fotime = datetime.strptime(fotime_str, '%H:%M').time()  # Adjust the format as per your needs
        except ValueError:

            return redirect('i_policy_details', id=id)

        if foname and fodate and fotime:
            retailpolicies_FollowUp.objects.create(
                retail=retail,
                foname=foname,
                fodate=fodate,
                fotime=fotime,

                
            )


            return redirect('i_policy_details', id=id)


        return redirect('i_policy_details', id=id)
    
    return HttpResponse("Invalid request", status=400)



def filter_policies(request):
    policies = retailpolicies.objects.all()

    # Get the start and end dates from request
    start_date = request.GET.get('start-date')
    end_date = request.GET.get('end-date')
    print(start_date)
    print(end_date)
    if start_date and end_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        policies = policies.filter(strtdate__gte=start_date, enddate__lte=end_date)

    print(policies)
    context = {'retailpolicies_data': policies}
    return render(request, 'xp/i_enqhome.html', context)



def Personal_Accident(request):
    inscat=inscategory.objects.all()
    polty=motorpoltype.objects.all()
    mtrpolcov=motorpolcoverage.objects.all()
    mtncb=motorncb.objects.all() 
    insurer=insurancecomp.objects.all()
    sumtype=suminstype.objects.all()
    ibranch=insurancebranch.objects.all()

    return render(request,'xp/personal_accident.html',{"inscat":inscat,"poltyp":polty,'mtrpolcov':mtrpolcov,'mtrncb':mtncb,'insurer':insurer,'sumtype':sumtype,'ibranch':ibranch})




def submit_personal_accident(request):


    if request.method == 'POST':
        try:
            # Debugging output for POST data
            for key, value in request.POST.items():
                print(f'{key}: {value}')

            # Collect data for `clients`
            cname = request.POST.get('field1_cname')
            caddress = request.POST.get('field1_caddress')
            ccontact = request.POST.get('field1_ccontact')
            cemail = request.POST.get('field1_cemail')


            #collect data for `personal accidents table`
            pincode=request.POST.get('field1_pincode')
            ins_category=request.POST.get('field3_category')
            age=request.POST.get('field1_age')
            policy_no=request.POST.get('field2_expolno')
            comp_name=request.POST.get('field3_inscomp')
            cont_person=request.POST.get('field2_contperson')
            comp_branch=request.POST.get('field3_insbranch')
            aadhar=request.POST.get('field2_aadhar')
            pan=request.POST.get('field2_pan')
            dor=request.POST.get('field2_dor')
            dob=request.POST.get('field2_dob')
            nominee_name=request.POST.get('field3_nominee_name')
            nominee_relationship=request.POST.get('field3_relationship')
            nominee_age=request.POST.get('field3_nom_age')
            amt_insured=request.POST.get('field3_amtpd')
            premium=request.POST.get('field3_premium')
            p_gst_value=request.POST.get('field3_gst_value')
            total_gst=request.POST.get('field3_total_gst')
            stdate=request.POST.get('field3_stdate')
            enddate=request.POST.get('field3_endate')

            print(ins_category)

            if not dor:
                return JsonResponse({'error': 'The "Date of Registration" (dor) field is required.'}, status=400)



            # Start transaction
            with transaction.atomic():
                # Save `clients`
                client = clients.objects.create(
                    cname=cname,
                    caddress=caddress or None,
                    ccontact=ccontact or None,
                    cemail=cemail or None,
                )

                # Save `personal accident `
                motor = personal_Accident.objects.create(
                    cid=client,
                    category=inscategory.objects.get(pk = ins_category) or None,
                    inscomp_name=insurancecomp.objects.get(pk = comp_name) or None,
                    ins_branch=insurancebranch.objects.get(pk = comp_branch) or None,
                    policy_no=policy_no or None,
                    contact_person=cont_person or None,
                    dateof_reg=dor or None,
                    pincode=pincode or None,
                    aadhar=aadhar or None,
                    pan_card=pan or None,
                    age=age or None,
                    dob=dob or None,
                    start_date=stdate or None,
                    end_date=enddate or None,
                    nominee_name=nominee_name or None,
                    relationship=nominee_relationship or None,
                    nominee_age=nominee_age or None,
                    amount_insured=amt_insured or None,
                    premium=premium or None,
                    p_gst=p_gst_value or None,
                    total_gst=total_gst or None,
                    uid=request.user  # <-- Assign the currently logged-in user


                )
            

            return redirect('ienquiry')

        except Exception as e:
            print(f'Error occurred: {e}')
            return JsonResponse({'error': 'An error occurred while processing the form. Please try again.'}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def Personal_acc_details(request, id):
    
    personal = get_object_or_404(personal_Accident, id=id)
    personal_accfollowups=personal_accident_FollowUp.objects.filter(personal_Acc=id)   

    data={
        "id":id,
        "cid":personal.cid,
        "category":personal.category,
        "inscomp_name":personal.inscomp_name,
        "ins_branch":personal.ins_branch,
        "contact_person":personal.contact_person,
        "dateof_reg":personal.dateof_reg,
        "pincode":personal.pincode,
        "policy_no":personal.policy_no,
        "aadhar":personal.aadhar,
        "pan_card":personal.pan_card,
        "age":personal.age,
        "dob":personal.dob,
        "nominee_name":personal.nominee_name,
        "nominee_age":personal.nominee_age,
        "relationship":personal.relationship,
        "amount_insured":personal.amount_insured,
        "premium":personal.premium,
        "p_gst":personal.p_gst,
        "total_gst":personal.total_gst,
        "start_date":personal.start_date,
        "end_date":personal.end_date,
    }
    return render(request,'xp/personal_accident_details.html',{'personal':data,'personal_accfollowups':personal_accfollowups})



def accident_renewal(request, id):

    inscat = inscategory.objects.all()
    polty = motorpoltype.objects.all()
    mtrpolcov = motorpolcoverage.objects.all()
    mtncb = motorncb.objects.all()
    insurer = insurancecomp.objects.all()
    sumtype = suminstype.objects.all()
    ibranch = insurancebranch.objects.all()
 
    # Retrieve the selected retail policy
    personal = personal_Accident.objects.get(id=id)
    personal.renewals=True
    personal.save()


    renewals = personal_Accident.objects.filter(
        uid=User.objects.get(id=request.user.id),
        end_date__gte=date.today()
    ).all().order_by('-end_date')

     # Prepopulate the form with the selected policy's details
    form_data = {
        "field1_cname": personal.cid.cname,
        "field1_ccontact": personal.cid.ccontact,
        "field1_cemail": personal.cid.cemail,
        "field1_caddress": personal.cid.caddress,
        "field1_age":personal.age,
        "field1_pincode":personal.pincode,
        "field2_aadhar":personal.aadhar,
        "field2_pan":personal.pan_card,
        "field2_contperson":personal.contact_person,
        "field3_nominee_name":personal.nominee_name,
        "field3_relationship":personal.relationship,
        "field3_nom_age":personal.nominee_age,



    }


    return render(request, 'xp/personal_accident.html', {
        "inscat": inscat,
        "poltyp": polty,
        "mtrpolcov": mtrpolcov,
        "mtrncb": mtncb,
        "insurer": insurer,
        "sumtype": sumtype,
        "ibranch": ibranch,
        "renewals": renewals,
        "form_data":form_data,  
    })



def personal_Acc_add_followup(request, id):
    retailpersonalfollowups = personal_accident_FollowUp.objects.all()
    if request.method == "POST":
        retail = get_object_or_404(personal_Accident, id=id)
        foname = request.POST.get('foname')
        fodate_str = request.POST.get('fodate')
        fotime_str = request.POST.get('fotime')
        # Ensure fodate is a valid datetime object
        try:
            fodate = datetime.strptime(fodate_str, '%Y-%m-%d')  # Adjust the format as per your needs
        except ValueError:

            return redirect('personal_accident_details', id=id)

        # Ensure fotime is a valid time object
        try:
            fotime = datetime.strptime(fotime_str, '%H:%M').time()  # Adjust the format as per your needs
        except ValueError:

            return redirect('personal_accident_details', id=id)

        if foname and fodate and fotime:
            personal_accident_FollowUp.objects.create(
                personal_Acc=retail,
                foname=foname,
                fodate=fodate,
                fotime=fotime,

                
            )

            print(retailpersonalfollowups)
            return redirect('personal_accident_details', id=id)


        return redirect('personal_accident_details', id=id)
    
    return HttpResponse("Invalid request", status=400)



def active_views(request, id, vid):
    active = get_object_or_404(confirmed_enquiry, vid=vid)  # Use correct model
    confirmed_fup = ConfirmedOrderFollowUp.objects.filter( confirmed_order__vid=vid)
    enquiry = get_object_or_404(Enquiry, id=id)

    uploaded_files = list(active.files.all())  # Convert queryset to list
    filess = list(enquiry.files.all())  # Convert queryset to list


    # Debugging Output
    if uploaded_files:
        print(uploaded_files[0].name)  # Print only if files exist
    else:
        print("No uploaded files found in ConfirmedEnquiry.")

    print("Files from Enquiry:", filess)

    return render(request, 'xp/active_view.html', {
        'id': id,
        'active': active,
        'filess': filess,
        'uploaded_files': uploaded_files,
        'confirmed_fup':confirmed_fup,
    })


def confirmed_active_add_followup(request, id,vid):
    followups = ConfirmedOrderFollowUp.objects.all()
    if request.method == "POST":
        confirmed = get_object_or_404(confirmed_enquiry, vid=vid)
        foname = request.POST.get('foname')
        fodate_str = request.POST.get('fodate')
        fotime_str = request.POST.get('fotime')
        
        # Ensure fodate is a valid datetime object
        try:
            fodate = datetime.strptime(fodate_str, '%Y-%m-%d')  # Adjust the format as per your needs
        except ValueError:

            return redirect('active_view', id=id, vid=vid)

        # Ensure fotime is a valid time object
        try:
            fotime = datetime.strptime(fotime_str, '%H:%M').time()  # Adjust the format as per your needs
        except ValueError:

            return redirect('active_view', id=id, vid=vid)

        if foname and fodate and fotime:
            ConfirmedOrderFollowUp.objects.create(
                confirmed_order=confirmed,
                foname=foname,
                fodate=fodate,
                fotime=fotime,

                
            )


            return redirect('active_view', id=id, vid=vid)


        return redirect('active_view', id=id, vid=vid)
    
    return HttpResponse("Invalid request", status=400)

import json
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.timezone import now
from .models import Enquiry, FollowUp, FollowUp_History, ConfirmedOrderFollowUp
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.timezone import now
import json
from datetime import datetime
from .models import (
    Enquiry, FollowUp, FollowUp_History,
    confirmed_enquiry, ConfirmedOrderFollowUp
)

def enquiry_followup(request):
    search_query = request.GET.get('search', '')

    


    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Extracting data from JSON request
            enquiry_id = data.get("enquiry_id")
            confirmed_order_id = data.get("confirmed_order_id")  # For active follow-ups
            foname = data.get("foname", "").strip()
            fodate = data.get("fodate")
            fotime = data.get("fotime")
            followup_type = data.get("followup_type")  # "enquiry" or "active"
            user = request.user if request.user.is_authenticated else None

            # Validate required fields
            if not foname or not fodate or not fotime:
                return JsonResponse({"success": False, "message": "All fields are required!"})

            # Parse date and time
            fodate_parsed = datetime.strptime(fodate, "%Y-%m-%d").date()
            fotime_parsed = datetime.strptime(fotime, "%H:%M").time()

            if followup_type == "enquiry":
                # Regular Enquiry Follow-Up
                if not enquiry_id:
                    return JsonResponse({"success": False, "message": "Enquiry ID is required!"})

                enquiry = Enquiry.objects.get(id=enquiry_id)
                followup = FollowUp.objects.create(
                    enquiry=enquiry,
                    foname=foname,
                    fodate=fodate_parsed,
                    fotime=fotime_parsed,
                    user=user
                )

                # Store in follow-up history
                FollowUp_History.objects.create(
                    enquiry=enquiry,
                    foname=foname,
                    fodate=fodate_parsed,
                    fotime=fotime_parsed,
                    created_at=now()
                )

            elif followup_type == "active":
                # Active Follow-Up (Confirmed Order)
                if not confirmed_order_id:
                    return JsonResponse({"success": False, "message": "Confirmed Order ID is required!"})

                confirmed_order = confirmed_enquiry.objects.get(vid=confirmed_order_id)
                ConfirmedOrderFollowUp.objects.create(
                    confirmed_order=confirmed_order,
                    foname=foname,
                    fodate=fodate_parsed,
                    fotime=fotime_parsed
                )
                 # Store in follow-up history
                FollowUp_History.objects.create(
                    confirmed_order=confirmed_order,  # ✅ Use the correct field name
                    foname=foname,
                    fodate=fodate_parsed,
                    fotime=fotime_parsed
                )

            return JsonResponse({"success": True, "message": "Follow-up saved successfully!"})

        except Enquiry.DoesNotExist:
            return JsonResponse({"success": False, "message": "Enquiry not found!"})
        except confirmed_enquiry.DoesNotExist:
            return JsonResponse({"success": False, "message": "Confirmed order not found!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    else:
        # Fetch all required data for rendering
        enquiries = Enquiry.objects.filter(is_confirmed=False)
        confirmed_orders = confirmed_enquiry.objects.all()
        # confirmed_followups = ConfirmedOrderFollowUp.objects.all()
        # followups = FollowUp.objects.all()
        followup_history = FollowUp_History.objects.all().order_by('-id')

        if search_query:
            followup_history = followup_history.filter(
                Q(foname__icontains=search_query) |
                Q(fodate__icontains=search_query) |
                Q(fotime__icontains=search_query) |
                Q(enquiry__companyname__icontains=search_query) |
                Q(confirmed_order__enquiry__companyname__icontains=search_query)
            )
        
        return render(request, 'xp/enq_followup.html', {
            "enquiries": enquiries,
            "confirmed_orders": confirmed_orders,  
            "search_query": search_query,
            "followup_history": followup_history,
        })


def retail_follow_up(request):
    search_query = request.GET.get('search', '')

    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Extracting data from JSON request
            enquiry_id = data.get("enquiry_id")
            confirmed_order_id = data.get("confirmed_order_id")  # For active follow-ups
            foname = data.get("foname", "").strip()
            fodate = data.get("fodate")
            fotime = data.get("fotime")
            followup_type = data.get("followup_type")  # "Retail" or "pac"
            user = request.user if request.user.is_authenticated else None

            # Validate required fields
            if not foname or not fodate or not fotime:
                return JsonResponse({"success": False, "message": "All fields are required!"})

            # Parse date and time
            fodate_parsed = datetime.strptime(fodate, "%Y-%m-%d").date()
            fotime_parsed = datetime.strptime(fotime, "%H:%M").time()

            if followup_type == "Retail":
                # Regular Enquiry Follow-Up
                if not enquiry_id:
                    return JsonResponse({"success": False, "message": "Enquiry ID is required!"})

                Retails = retailpolicies.objects.get(id=enquiry_id)
                followup = retailpolicies_FollowUp.objects.create(
                    retail=Retails,
                    foname=foname,
                    fodate=fodate_parsed,
                    fotime=fotime_parsed,
                    user=user
                )

                # Store in follow-up history
                Retail_FollowUp_History.objects.create(
                    Retail=Retails,
                    foname=foname,
                    fodate=fodate_parsed,
                    fotime=fotime_parsed,
                    created_at=now()
                )

                

            elif followup_type == "pac":
                # Active Follow-Up (Confirmed Order)
                if not confirmed_order_id:
                    return JsonResponse({"success": False, "message": "Confirmed Order ID is required!"})

                personal_acc = personal_Accident.objects.get(id=confirmed_order_id)
                personal_accident_FollowUp.objects.create(
                    personal_Acc=personal_acc,
                    foname=foname,
                    fodate=fodate_parsed,
                    fotime=fotime_parsed
                )

                # Store in follow-up history
                Retail_FollowUp_History.objects.create(
                    Personal=personal_acc,
                    foname=foname,
                    fodate=fodate_parsed,
                    fotime=fotime_parsed,
                    created_at=now()
                )

               

            return JsonResponse({"success": True, "message": "Follow-up saved successfully!"})

        except Enquiry.DoesNotExist:
            return JsonResponse({"success": False, "message": "Enquiry not found!"})
        except confirmed_enquiry.DoesNotExist:
            return JsonResponse({"success": False, "message": "Confirmed order not found!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    else:
        # Fetch all required data for rendering
        retailss = retailpolicies.objects.all()
        personalss = personal_Accident.objects.all()
        followup_retail=Retail_FollowUp_History.objects.all().order_by('-id')


        if search_query:
            followup_retail = followup_retail.filter(
                Q(foname__icontains=search_query) |  # Search Follow-Up Name
                Q(fodate__icontains=search_query) |  # Search Follow-Up Date
                Q(fotime__icontains=search_query) |  # Search Follow-Up Time
                Q(Retail__cid__cname__icontains=search_query) |  # ✅ Search Client Name in Retail Policies
                Q(Personal__cid__cname__icontains=search_query)  # ✅ Search Client Name in Personal Accident
            )


        return render(request, 'xp/retail_followup.html', {
            "retailss": retailss,
            "personalss": personalss,
            "search_query":search_query,
            "followup_retail":followup_retail,
        })
    

def get_company_suggestions(request):
    query = request.GET.get('query', '')
    if query:
        companies = Enquiry.objects.filter(companyname__icontains=query)[:10]
        data = [{'id': company.id, 'companyname': company.companyname} for company in companies]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

def get_company_details(request):
    company_id = request.GET.get('id', '')
    try:
        company = Enquiry.objects.get(id=company_id)
        data = {
            'customername': company.customername,
            'email': company.email,
            'contact': company.contact,
            'location': company.location,
            'remarks': company.remarks,
            'refrence':company.refrence,
            'subproduct':company.subproduct,
            'status': company.status,
            'product_id': company.products.id if company.products else '',
            'executive_id': company.executive.id if company.executive else ''
        }
        return JsonResponse(data)
    except Enquiry.DoesNotExist:
        return JsonResponse({})
    



import pandas as pd
from django.shortcuts import redirect
from django.contrib import messages
from .models import Enquiry, Products, Executive
from django.utils.timezone import now
from datetime import datetime


def upload_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        try:
            # Read the Excel file
            df = pd.read_excel(excel_file)
        except Exception as e:
            messages.error(request, f"Invalid file format: {e}")
            return redirect('confirmedorderss')

        # ✅ Map Executive using the logged-in user's username
        try:
            executive = Executive.objects.get(name=request.user.username)
        except Executive.DoesNotExist:
            messages.error(request, "No Executive linked to this user. Please contact admin.")
            return redirect('confirmedorderss')

        # ✅ Iterate through rows and create Enquiry + Confirmed Enquiry
        for index, row in df.iterrows():
            companyname = str(row.get('companyname')).strip()
            customername = str(row.get('customername')).strip()
            contact = str(row.get('contact')).strip()
            policy_type = str(row.get('policy Type')).strip()
            closuredate = row.get('closuredate')

            # ✅ Check if Product exists, if not create it
            product, created = Products.objects.get_or_create(name=policy_type)

            # ✅ Convert closuredate to DateField format (Fixing Date Issue)
            if pd.notnull(closuredate):
                try:
                    closuredate = pd.to_datetime(closuredate, errors='coerce').date()
                except Exception:
                    closuredate = None
            else:
                closuredate = None

            # ✅ Create Enquiry if not already created
            enquiry = Enquiry.objects.create(
                companyname=companyname,
                customername=customername,
                contact=contact,
                products=product,
                closuredate=closuredate,
                executive=executive,
                created_by=request.user,
                status="N/A",
                remarks="N/A"
            )

            # ✅ Now also Insert the Confirmed Enquiry with Foreign Key Reference
            vid = str(row.get('vid')).strip()
            startdate = row.get('startdate')
            enddate = row.get('enddate')
            flag = str(row.get('flag')).strip()
            renewal_days = int(row.get('renewal_days'))
            sum_amount = str(row.get('sum_amount')).strip()
            premium_amount = str(row.get('premium_amount')).strip()
            Gst_amount = str(row.get('Gst_amount')).strip()

            # ✅ Convert Date Fields
            try:
                startdate = pd.to_datetime(startdate, errors='coerce').date()
                enddate = pd.to_datetime(enddate, errors='coerce').date()
            except Exception:
                startdate = None
                enddate = None

            # ✅ Avoid Duplicate Confirmed Enquiries with the same vid
            if not confirmed_enquiry.objects.filter(vid=vid).exists():
                confirmed_enquiry.objects.create(
                    created_by=request.user,
                    enquiry=enquiry,  # ✅ Linking Enquiry as ForeignKey
                    vid=vid,
                    startdate=startdate,
                    enddate=enddate,
                    flag=flag,
                    policy_type=policy_type,
                    renewal_days=renewal_days,
                    sum_amount=sum_amount,
                    premium_amount=premium_amount,
                    Gst_amount=Gst_amount
                )
                # ✅ As soon as Confirmed Enquiry is created, update is_confirmed=True in Enquiry
                enquiry.is_confirmed = True
                enquiry.save(update_fields=['is_confirmed'])
            

        messages.success(request, "Enquiries and Confirmed Enquiries created successfully from the Excel file.")
        return redirect('confirmedorderss')

    else:
        messages.error(request, "Invalid request.")
        return redirect('confirmedorderss')
