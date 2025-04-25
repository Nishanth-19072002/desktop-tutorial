from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import User

class Products(models.Model):
    name = models.CharField(max_length=100)
    

    def __str__(self):  # Correct method name
        return self.name

class Executive(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class FileUploadModel(models.Model):
    file = models.FileField(upload_to='uploads/')
    name = models.CharField(max_length=255)  
    def __str__(self):
        return self.name
    
# In models.py

class Enquiry(models.Model):
    STATUS_CHOICES = [
        ('1', 'HOT'),
        ('2', 'WARM'),
        ('3', 'COLD'),
    ]
  
    companyname = models.CharField(max_length=30, default='')
    customername = models.CharField(max_length=20, default='')


    
    refrence = models.CharField(max_length=20, default='',blank=True)
    email = models.EmailField()
    contact = models.IntegerField()
    location = models.CharField(max_length=100, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='')
    products = models.ForeignKey(Products, on_delete=models.CASCADE, default=1)  # Make sure product with id=1 exists
    subproduct = models.CharField(max_length=20, default='',blank=True)
    closuredate = models.DateField(null=True, blank=True)
    executive = models.ForeignKey(Executive, on_delete=models.CASCADE, null=False, blank=False)
    files = models.ManyToManyField(FileUploadModel, blank=True)
    remarks = models.TextField(max_length=100, default='', blank=True)
    flag = models.TextField(max_length=200, default='', blank=True)
    enqtype = models.CharField(max_length=20, default='',blank=True)
    is_confirmed = models.BooleanField(default=False) 
    created_at = models.DateTimeField(auto_now_add=True)
    is_lost = models.BooleanField(default=False)
    is_reverted = models.BooleanField(default=False) 
    is_relegated=models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 
    lostdate = models.DateField(null=True, blank=True)

    lost_renewal_days = models.IntegerField(default=30)  # No. of days before renewal

    def is_lost_for_renewal(self):
        today = now().date()
        lost_renewal_date = self.lostdate - timedelta(days=self.lost_renewal_days)
        return today >= lost_renewal_date

    
    def __str__(self):
        return f"Enquiry from {self.companyname}"

    
class RevertRemark(models.Model):
    enquiry = models.ForeignKey(Enquiry, related_name='revert_remarks', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Remark for {self.enquiry.companyname} - {self.created_at}"
    

class quotation(models.Model):
    qid= models.ForeignKey(Enquiry, on_delete=models.CASCADE)
    quote=models.FileField(upload_to='quotes/', blank=True, null=True)
    baseamount=models.DecimalField(max_digits=15, decimal_places=2, default=0)
    boq=models.FileField(upload_to='boqs/', blank=True, null=True)
    finalamount=models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True) 
    
 
    def __str__(self):
        return f"Quotation for {self.qid}"

from datetime import date, timedelta


class FollowUp(models.Model):
    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE, related_name="followups")
    foname = models.CharField(max_length=255)
    fodate = models.DateField()
    fotime = models.TimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Calculate the notification date as one day prior to the fodate
        self.notify_on = self.fodate - timedelta(days=1)
        super().save(*args, **kwargs)



class ConfirmedOrder(models.Model):
    quotation = models.ForeignKey(quotation, on_delete=models.CASCADE)
    project_closing_date = models.DateField()
    workorder = models.FileField(upload_to='workorders/', blank=True, null=True)
    boq = models.FileField(upload_to='boqs/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True) 
    
    # Make 'enquiry' nullable for existing rows
    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Confirmed Order for Enquiry #{self.enquiry.id if self.enquiry else 'No Enquiry'}"

from django import forms
class ConfirmedOrderForm(forms.ModelForm):
    class Meta:
        model = ConfirmedOrder
        fields = ['quotation', 'project_closing_date', 'workorder', 'boq']
        widgets = {
            'project_closing_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(ConfirmedOrderForm, self).__init__(*args, **kwargs)
        self.fields['quotation'].queryset = quotation.objects.all() 


class ConfirmedOrderFollowUp(models.Model):
    confirmed_order = models.ForeignKey(
        'confirmed_enquiry',
        on_delete=models.CASCADE,
        related_name='followups',
        help_text="The confirmed order associated with this follow-up"
    )
    foname = models.CharField(max_length=20, default='', help_text="Name associated with the follow-up")
    fodate = models.DateField(help_text="Date of the follow-up")
    fotime = models.TimeField(help_text="Time of the follow-up")
    entrydate = models.DateTimeField(default=timezone.now, help_text="Timestamp for when this entry was created or modified")

    def __str__(self):
        return f"Follow-up by {self.foname} on {self.fodate} at {self.fotime}"
    

from django.utils.timezone import now

class confirmed_enquiry(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 
    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE, null=True, blank=True)
    revert = models.BooleanField(default=False)
    relegate = models.BooleanField(default=False)
    vid = models.CharField(max_length=20, unique=True) 
    # New fields 
    startdate = models.DateField(null=True, blank=True)
    enddate = models.DateField(null=True, blank=True)
    flag = models.CharField(max_length=255, null=True, blank=True)
    policy_type = models.CharField(max_length=255, null=True, blank=True)
    renewal_days = models.IntegerField(default=30)  # No. of days before renewal
    renewal_flag = models.BooleanField(default=False)  # To indicate renewal visibility
    sum_amount=models.CharField(max_length=20,null=True, blank=True) 
    premium_amount=models.CharField(max_length=20,null=True, blank=True) 
    cal_gst=models.CharField(max_length=20,null=True, blank=True) 
    Gst_amount=models.CharField(max_length=20,null=True, blank=True) 
    files = models.ManyToManyField(FileUploadModel, blank=True)
    #newly added fields
    client_name= models.CharField(max_length=100, null=True, blank=True)
    client_phone= models.CharField(max_length=100, null=True, blank=True)
    client_email= models.EmailField( null=True, blank=True)
    tpa_name= models.CharField(max_length=100, null=True, blank=True)
    tpa_phone= models.CharField(max_length=100, null=True, blank=True)
    tpa_email= models.EmailField( null=True, blank=True)
    vrd_name= models.CharField(max_length=100, null=True, blank=True)
    vrd_phone= models.CharField(max_length=100, null=True, blank=True)
    vrd_email= models.EmailField( null=True, blank=True)

    def is_due_for_renewal(self):
        today = now().date()
        renewal_date = self.enddate - timedelta(days=self.renewal_days)
        return today >= renewal_date

    def __str__(self):
        if self.enquiry:
            return f"Confirmed Enquiry ID: {self.enquiry.id}"
        else:
            return "Confirmed Enquiry (No Enquiry Assigned)"
    
class FollowUp_History(models.Model):
    enquiry = models.ForeignKey("Enquiry", on_delete=models.CASCADE, null=True, blank=True)  # Link to enquiry (nullable)
    confirmed_order = models.ForeignKey("confirmed_enquiry", on_delete=models.CASCADE, null=True, blank=True)  # Link to confirmed order (nullable)
    foname = models.TextField()  # Follow-up Remarks
    fodate = models.DateField()  # Follow-up Date
    fotime = models.TimeField()  # Follow-up Time
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    def __str__(self):
        return f"Follow-Up (Enquiry: {self.enquiry.id if self.enquiry else 'N/A'}, Confirmed Order: {self.confirmed_order.vid if self.confirmed_order else 'N/A'})"


########################################################################################################################################################
############ v retail ############### i crm ######################################

from django.db.models.signals import post_save


uzones = (
    ("1", "BNG"),
    ("2", "SIRSI"),
    ("3", "HUBLI"),
    ("4", "DHARWARD"),
    ("5", "JAYSINPUR"),
    ("6", "MYSORE"),
    ("7", "MANGALORE"),
    ("8", "UDUPI"),
    ("9", "KUNDAPURA"),
    ("10","OTHERS"),
      
)
   


# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     contatcno = models.CharField(max_length=15,default="",null=True,blank=True)
#     userzone=models.CharField(max_length = 30,choices=uzones,default = '1')

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()


class clients(models.Model): 
    DEFAULT_PK=1
    cname=models.CharField(max_length=100,default="",null=True,blank=True)
    caddress=models.CharField(max_length=500,default="",null=True,blank=True)
    ccontact=models.CharField(max_length=15,default="",null=True,blank=True)
    cemail=models.CharField(max_length=100,default="",null=True,blank=True)
    
class inscategory(models.Model):
    DEFAULT_PK=1
    insname=models.CharField(max_length=100,default="",null=True,blank=True)
    
class motorpolcoverage(models.Model):
    polname=models.CharField(max_length=100,default="",null=True,blank=True)

class motorpoltype(models.Model):
    pltname=models.CharField(max_length=100,default="",null=True,blank=True)

class motorncb(models.Model):
    DEFAULT_PK=1
    ncbno=models.IntegerField(default=0)
    
class insurancecomp(models.Model):
    DEFAULT_PK=1
    insname=models.CharField(max_length=200,default="",null=True,blank=True)
    
class insurancebranch(models.Model):
    DEFAULT_PK=1
    inscomp=models.ForeignKey(insurancecomp,on_delete=models.CASCADE)
    insbranch=models.CharField(max_length=200,default="",null=True,blank=True)
    branch_pincode = models.CharField(max_length=20, null=True, blank=True) 

class suminstype(models.Model):
    DEFAULT_PK=1
    name=models.CharField(max_length=100,default="",null=True,blank=True)


class rccopymodel(models.Model):
    file = models.FileField(upload_to='uploads/rccopy/')  # Adjust the upload path as needed
    name = models.CharField(max_length=255)  

    def __str__(self):
        return self.name 



class motorpol(models.Model): 
    cid=models.ForeignKey(clients,on_delete=models.CASCADE)
    expolno=models.CharField(max_length=50,default="",null=True,blank=True)
    engineno=models.CharField(max_length=50,default="",null=True,blank=True)
    chassisno=models.CharField(max_length=50,default="",null=True,blank=True)
    dor=models.DateField(default=date.today)
    ncb=models.ForeignKey(motorncb,on_delete=models.CASCADE,default=motorncb.DEFAULT_PK)
    regno=models.CharField(max_length=100,default="",null=True,blank=True)
    rtocity=models.CharField(max_length=300,default="",null=True,blank=True)
    polcov=models.ForeignKey(motorpolcoverage,on_delete=models.CASCADE)
    poltype=models.ForeignKey(motorpoltype,on_delete=models.CASCADE)
    rccopy = models.ManyToManyField(rccopymodel, blank=True, related_name='motorpols')
    tpname=models.ForeignKey(insurancecomp,on_delete=models.CASCADE,default=insurancecomp.DEFAULT_PK)
    makemodel=models.CharField(max_length=200,default="",null=True,blank=True)
    idv=models.FloatField(default=0)
    
class marinepol(models.Model):
    cid=models.ForeignKey(clients,on_delete=models.CASCADE)
    expolno=models.CharField(max_length=50,default="",null=True,blank=True)
    lrno=models.CharField(max_length=50,default="",null=True,blank=True)
    consignmentval=models.FloatField(default=0)
    
class firepol(models.Model):
    cid=models.ForeignKey(clients,on_delete=models.CASCADE)
    expolno=models.CharField(max_length=100,default="",null=True,blank=True)
    asstval=models.FloatField(default=0)

class shopkeeperspol(models.Model): 
    cid=models.ForeignKey(clients,on_delete=models.CASCADE)
    expolno=models.CharField(max_length=100,default="",null=True,blank=True)
    stkval=models.FloatField(default=0)
    
class mediclaimpol(models.Model): 
    cid=models.ForeignKey(clients,on_delete=models.CASCADE)
    expolno=models.CharField(max_length=100,default="",null=True,blank=True)
    age=models.IntegerField(default=0,null=True,blank=True)
    suminsured=models.FloatField(default=0)
    sitype=models.ForeignKey(suminstype,on_delete=models.CASCADE,default=suminstype.DEFAULT_PK)

    
class wcpol(models.Model):
    cid=models.ForeignKey(clients,on_delete=models.CASCADE)
    expolno=models.CharField(max_length=100,default="",null=True,blank=True)
    empcount=models.IntegerField(default=0,null=True,blank=True)
    salary=models.FloatField(default=0)
    placeofwork=models.CharField(max_length=100,default="",null=True,blank=True)
    naturework=models.CharField(max_length=100,default="",null=True,blank=True)


        
class policycopy(models.Model):
    file = models.FileField(upload_to='uploads/policycopy/')  # Adjust the upload path as needed
    name = models.CharField(max_length=255)  

    def __str__(self):
        return self.name 
    
class retailpolicies(models.Model): 
    uid=models.ForeignKey(User,on_delete=models.CASCADE)
    cid=models.ForeignKey(clients,on_delete=models.CASCADE)
    retpol=models.ForeignKey(inscategory,on_delete=models.CASCADE,default=inscategory.DEFAULT_PK)
    inscomp=models.ForeignKey(insurancecomp,on_delete=models.CASCADE)
    insbranch=models.ForeignKey(insurancebranch,on_delete=models.CASCADE,default=insurancebranch.DEFAULT_PK)
    strtdate=models.DateField(default=date.today)
    enddate=models.DateField(default=date.today)
    amtpd=models.FloatField(default=0)
    gstval=models.FloatField(default=0)
    amount_insured=models.FloatField(default=0)
    amtpdgst=models.FloatField(default=0)
    polno=models.CharField(max_length=50,default="",null=True,blank=True)
    newpolcopy=models.ManyToManyField(policycopy, blank=True, related_name='policycopy')
    rtcreated_at = models.DateField(auto_now_add=True)
    renewals=models.BooleanField(default=False)
    

    
class retailpolicies_FollowUp(models.Model):
    retail = models.ForeignKey(retailpolicies, on_delete=models.CASCADE, related_name="followups")
    foname = models.CharField(max_length=255)
    fodate = models.DateField()
    fotime = models.TimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Calculate the notification date as one day prior to the fodate
        self.notify_on = self.fodate - timedelta(days=1)
        super().save(*args, **kwargs)


class personal_Accident(models.Model):
    uid=models.ForeignKey(User,on_delete=models.CASCADE)
    cid=models.ForeignKey(clients,on_delete=models.CASCADE)
    category=models.ForeignKey(inscategory,on_delete=models.CASCADE,default=inscategory.DEFAULT_PK)
    inscomp_name=models.ForeignKey(insurancecomp,on_delete=models.CASCADE)
    ins_branch=models.ForeignKey(insurancebranch,on_delete=models.CASCADE)
    policy_no=models.CharField(max_length=50,default="",blank=True,null=True)
    contact_person=models.CharField(max_length=50,default="",blank=True,null=True)
    dateof_reg=models.DateField(default=date.today,blank=True,null=True)
    pincode=models.CharField(max_length=50,default="",blank=True,null=True)
    aadhar=models.CharField(max_length=50,default="",blank=True,null=True)
    pan_card=models.CharField(max_length=50,default="",blank=True,null=True)
    age=models.IntegerField(blank=True,null=True)
    dob=models.DateField(default=date.today,blank=True,null=True)
    nominee_name=models.CharField(max_length=50,default="",blank=True,null=True)
    relationship=models.CharField(max_length=50,default="",blank=True,null=True)
    nominee_age=models.IntegerField(blank=True,null=True)
    amount_insured=models.FloatField(blank=True,null=True)
    premium=models.FloatField(blank=True,null=True)
    p_gst=models.FloatField(blank=True,null=True)
    total_gst=models.FloatField(blank=True,null=True)
    start_date=models.DateField(default=date.today)
    end_date=models.DateField(default=date.today)
    renewals=models.BooleanField(default=False)


    
class personal_accident_FollowUp(models.Model):
    personal_Acc = models.ForeignKey(personal_Accident, on_delete=models.CASCADE, related_name="followups")
    foname = models.CharField(max_length=255)
    fodate = models.DateField()
    fotime = models.TimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Calculate the notification date as one day prior to the fodate
        self.notify_on = self.fodate - timedelta(days=1)
        super().save(*args, **kwargs)


from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE, null=True, blank=True)
    client= models.ForeignKey(clients, on_delete=models.CASCADE, null=True, blank=True)
    personal= models.ForeignKey(personal_Accident, on_delete=models.CASCADE, null=True, blank=True)
    retail= models.ForeignKey(retailpolicies, on_delete=models.CASCADE, null=True, blank=True)
    policy_no=models.CharField(max_length=50, null=True, blank=True)  # Change to CharField to store policyno 
    vid = models.CharField(max_length=50, null=True, blank=True)  # Change to CharField to store VID
     
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.message}"



class Retail_FollowUp_History(models.Model):
    Retail = models.ForeignKey("retailpolicies", on_delete=models.CASCADE, null=True, blank=True)  # Link to enquiry (nullable)
    Personal = models.ForeignKey("personal_Accident", on_delete=models.CASCADE, null=True, blank=True)  # Link to confirmed order (nullable)
    foname = models.TextField()  # Follow-up Remarks
    fodate = models.DateField()  # Follow-up Date
    fotime = models.TimeField()  # Follow-up Time
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    def __str__(self):
        return f"Follow-Up (Retail: {self.Retail.id if self.Retail else 'N/A'}, Personal: {self.Personal.id if self.Personal else 'N/A'})"
