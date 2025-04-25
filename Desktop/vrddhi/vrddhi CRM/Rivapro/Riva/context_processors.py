from django.shortcuts import get_object_or_404
from .models import ConfirmedOrderFollowUp, Enquiry, FollowUp, Notification, personal_Accident, personal_accident_FollowUp, retailpolicies, retailpolicies_FollowUp
from django.utils import timezone
from datetime import date, timedelta
from django.utils.timezone import now

from itertools import chain

from itertools import chain
from django.db.models import Value, CharField

# def followups_context(request):
#     today = timezone.localdate()
#     one_day_before = today - timedelta(days=1)

#     # Query regular follow-ups
#     followups_today = FollowUp.objects.filter(fodate=today).order_by('-fodate', '-fotime').annotate(type=Value('regular', output_field=CharField()))
#     followups_one_day_before = FollowUp.objects.filter(fodate=one_day_before).order_by('-fodate', '-fotime').annotate(type=Value('regular', output_field=CharField()))
#     followups = followups_today | followups_one_day_before

    

#     # Combine the querysets

#     # Total count
#     return {
#         'followupss': followups,  
#     }

from django.utils import timezone
from datetime import timedelta
from django.db.models import Value, CharField
from django.contrib.auth.models import AnonymousUser

def global_notifications(request):

    current_user = request.user

    # 🔹 Ensure the user is authenticated before querying
    if isinstance(current_user, AnonymousUser) or not current_user.is_authenticated:
        return {
            'notifications': [],  # Empty notifications if not authenticated
            'followups': [],
        }

    today = timezone.localdate()

    # ✅ Fetch only relevant orders based on who created them
    if current_user.is_superuser:
        confirmed_orders = Enquiry.objects.filter(is_confirmed=True)
        lost_orders = Enquiry.objects.filter(is_lost=True)
    else:
        confirmed_orders = Enquiry.objects.filter(is_confirmed=True, created_by=current_user)
        lost_orders = Enquiry.objects.filter(is_lost=True, created_by=current_user)

    confirmed_orders_due_for_renewal = []

    # ✅ Loop through orders and create notifications based on 'created_by'
    for order in confirmed_orders:
        for confirmed_entry in order.confirmed_enquiry_set.all():
            renewal_date = confirmed_entry.enddate - timedelta(days=confirmed_entry.renewal_days)
            if today >= renewal_date and not confirmed_entry.renewal_flag:
                confirmed_orders_due_for_renewal.append(confirmed_entry)

                # ✅ Create notification only for the user who created the enquiry
                Notification.objects.get_or_create(
                    user=order.created_by,  # 🔥 Correct User (NOT current_user)
                    vid=confirmed_entry.vid,
                    enquiry=confirmed_entry.enquiry,
                    message=f"{confirmed_entry.enquiry.companyname} :{confirmed_entry.vid} renewal on {confirmed_entry.enddate}"
                )

                # ✅ If 'revert' is True, delete the notification
                if confirmed_entry.revert:
                    Notification.objects.filter(vid=confirmed_entry.vid).delete()

    # ✅ Now handle policies that need renewal
    renewal_date = today + timedelta(days=30)

    # 🔥 Handle Retail Policies
    renewal_policies = retailpolicies.objects.filter(
        enddate__lte=renewal_date, enddate__gte=today
    ).order_by('-id')

    for policy in renewal_policies:
        Notification.objects.get_or_create(
            user=policy.uid,  # 🔥 Correct User (NOT current_user)
            retail=policy,
            policy_no=policy.polno,
            message=f"{policy.cid.cname} : {policy.polno} renewal on {policy.enddate}.",
        )
        if policy.renewals:
            Notification.objects.filter(policy_no=policy.polno).delete()

    # 🔥 Handle Personal Accident Policies
    personal_acc = personal_Accident.objects.filter(
        end_date__lte=renewal_date, end_date__gte=today
    ).order_by('-id')

    for policy in personal_acc:
        Notification.objects.get_or_create(
            user=policy.uid,  # 🔥 Correct User (NOT current_user)
            personal=policy,
            policy_no=policy.policy_no,
            message=f"{policy.cid.cname} : {policy.policy_no} renewal on {policy.end_date}.",
        )
        if policy.renewals:
            Notification.objects.filter(policy_no=policy.policy_no).delete()

    # ✅ Fetch only today's and future follow-ups
    today = date.today()
    tomorrow = today + timedelta(days=1)

    followups = FollowUp.objects.filter(fodate__gte=today, fodate__lte=tomorrow)
    confirmed_followups = ConfirmedOrderFollowUp.objects.filter(fodate__gte=today, fodate__lte=tomorrow)
    retail = retailpolicies_FollowUp.objects.filter(fodate__gte=today, fodate__lte=tomorrow)
    personal = personal_accident_FollowUp.objects.filter(fodate__gte=today, fodate__lte=tomorrow)

    # ✅ Fetch only notifications for the logged-in user
    notifications = Notification.objects.filter(user=current_user, is_read=False).order_by('-created_at')


    # Handle lost orders due for renewal
    lost_orders_due_for_renewal = [order for order in lost_orders if order.is_lost_for_renewal()]

    # ✅ Create notification for lost orders
    for lost in lost_orders_due_for_renewal:
        Notification.objects.get_or_create(
            user=current_user,
            enquiry=lost,
            message=f"Lost {lost.companyname}renewal on {lost.lostdate}."
        )
        # ✅ Delete notification if lost date is in the past
        if lost.lostdate < today:
            Notification.objects.filter(enquiry=lost).delete()


    return {
        'notifications': notifications,
        'followups': followups,
        'confirmed_followups': confirmed_followups,
        'retail': retail,
        'personal': personal,
    }
