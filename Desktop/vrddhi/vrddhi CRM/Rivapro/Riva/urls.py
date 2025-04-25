from .import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import enquiry_details
from django.contrib.auth.views import LoginView, LogoutView
from . import exportviews


urlpatterns = [
    
    path('Home', views.Home, name='Home'),
    path('enquiry/', views.enquiry_view, name='newenquirypage'),
    path('enqhome/', views.enq_home, name='enquries'),
    path('renewal/', views.Renewals, name='renewals'),    
    path('past-policy/', views.Past_policies, name='past_policies'),    

    path('Enq-followup/',views.enquiry_followup,name='follow_up'),

    path('get_company_suggestions/', views.get_company_suggestions, name='get_company_suggestions'),
    path('get_company_details/', views.get_company_details, name='get_company_details'),



    path('Icrm/', views.Icrm, name='icrm'),    
######################################################################################## ICRM ########################
    # path('Ienquiry/', views.I_enquiry_view, name='i_newenquirypage'),
    path('Ienqhome/', views.I_enq_home, name='ienquiry'),
    path('Irenewal/', views.I_Renewals, name='i_renewals'),    
    path('I_dashboard/', views.I_dashboard, name='i_dashboard'),
    path('I_add_enq/', views.I_add_enquiry, name='i_add_enquiry'),
    path('submit_form/', views.i_submit_form_vehicle, name='submit_form_vehicle'),
    path('policy/<int:id>/details/', views.policy_details, name='i_policy_details'),
    path('I_add_enq/<int:cid>', views.I_add_renewal, name='i_add_renewal'),
    path('retail-past-policy/', views.retail_Past_policy, name='retail_past_policies'),    

    path('policy/<int:id>/add-followup/', views.retail_policy_add_followup, name='retail_add_followup'),
    
    path('filter/', views.filter_policies, name='filter_policies'),
    path('renewal_filter/', views.Renewal_filter_policies, name='renewal_filter_policies'),
    path('personal-accident/', views.Personal_Accident, name='personal_accident'),
    path('submit-personal-accident/', views.submit_personal_accident, name='submit_pa'),
    path('pa/<int:id>/details/', views.Personal_acc_details, name='personal_accident_details'),
    path('accident-renew/<int:id>', views.accident_renewal, name='accident_renew'),
    path('personal_Acc/<int:id>/add-followups/', views.personal_Acc_add_followup, name='personal_add_followup'),

    path('Retail/add-followup/', views.retail_follow_up, name='retail_follow_up'),





####################################################################################
    path('add/', views.add_data, name='add_data'),
    path('enquiry/<int:id>/details/', views.enquiry_details, name='enquiry_details'),
    path('lostorders/', views.lost_orders_view, name='lost_orders'),
    path('enquiry/<int:id>/details/push-to-lost-order/', views.push_to_lost_order, name='push_to_lost_order'),
    path('lost-orders/delete/<int:id>/', views.delete_lost_order, name='deletelostorder'),
    path('enquiry/<int:id>/retrieve/', views.retrieve_lost_order, name='retrievelostorder'),
    path('edit-enquiry/<int:enquiry_id>/', views.edit_enquiry, name='edit-enquiry'),
    path('confirmed_orders/', views.confirmed_orders, name='confirmedorderss'),
    path('enquiry/<int:id>/add-followup/', views.add_followup, name='add_followup'),
    path('push-to-lost-order/<int:enquiry_id>/<str:vid>/', views.push_to_lost_order_from_confirmed, name='push_to_lost_order_from_confirmed'),
    path('confirmed/<int:enquiry_id>/<str:quotation_no>/', views.add_confirmed_order_followup, name='add_confirmed_order_followup'),
    path('', LoginView.as_view(template_name='app/login.html'), name='login'), 
    path('', LogoutView.as_view(template_name='app/logout.html'), name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('active/<int:id>/<str:vid>/details/', views.active_views, name='active_view'),

     
    path('confirmed/<int:id>/<str:vid>/add-followup/', views.confirmed_active_add_followup, name='confirmed_add_followup'),



#######################################################################################################################################


    path('enquiry/revert/<int:enquiry_id>/', views.revert_to_enquiries, name='revert_to_enquiries'),
  
    path('export/details-enquiries/<int:enquiry_id>/pdf/', views.export_pdf_details, name='export_details_enquiries_pdf'),
    path('export/confirmed-enquiries/pdf/', views.export_confirmed_orders_pdf, name='export_confirmed_orders_pdfpage'),



    path('export/confirmed-orders/csv/', exportviews.export_confirmed_orders_csv, name='export_confirmed_orders_csv'),
    path('export/confirmed-orders/xlsx/', exportviews.export_confirmed_orders_xlsx, name='export_confirmed_orders_xlsx'),
    path('export/confirmed-orders/pdf/', exportviews.export_confirmed_orders_pdf, name='export_confirmed_orders_pdf'),


    path('export-lost-enquiries-csv/', exportviews.export_lost_enquiries_csv, name='export_lost_enquiries_csv'),
    path('export-lost-enquiries-xlsx/', exportviews.export_lost_enquiries_xlsx, name='export_lost_enquiries_xlsx'),
    path('export-lost-enquiries-pdf/', exportviews.export_lost_enquiries_pdf, name='export_lost_enquiries_pdf'),



    path('export/enquiries/csv/', exportviews.export_enquiries_csv, name='export_enquiries_csv'),
    path('export/enquiries/pdf/', exportviews.export_enquiries_pdf, name='export_enquiries_pdf'),
    path('export/enquiries/xlsx/', exportviews.export_enquiries_xlsx, name='export_enquiries_xlsx'),
    


    path('export_confirmed_renewals_csv/', exportviews.export_confirmed_renewals_csv, name='export_confirmed_renewals_csv'),
    path('export_confirmed_renewals_xlsx/', exportviews.export_confirmed_renewals_xlsx, name='export_confirmed_renewals_xlsx'),
    path('export_confirmed_renewals_pdf/', exportviews.export_confirmed_renewals_pdf, name='export_confirmed_renewals_pdf'),


    path('export_past_policies_csv/', exportviews.export_past_policies_csv, name='export_past_policies_csv'),
    path('export_past_policies_xlsx/', exportviews.export_past_policies_xlsx, name='export_past_policies_xlsx'),
    path('export_past_policies_pdf/', exportviews.export_past_policies_pdf, name='export_past_policies_pdf'),


    path('export/enq_home/csv/', exportviews.export_enq_home_csv, name='export_enq_home_csv'),
    path('export/enq_home/xlsx/', exportviews.export_enq_home_xlsx, name='export_enq_home_xlsx'),
    path('export/enq_home/pdf/', exportviews.export_enq_home_pdf, name='export_enq_home_pdf'),


    path('export/i_renewals/csv/', exportviews.i_renewals_export_csv, name='i_renewals_export_csv'),
    path('export/i_renewals/xlsx/', exportviews.i_renewals_export_xlsx, name='i_renewals_export_xlsx'),
    path('export/i_renewals/pdf/', exportviews.i_renewals_export_pdf, name='i_renewals_export_pdf'),


    path('export/csv/',  exportviews.export_retail_past_policy_csv, name='export_csv_retail_past'),
    path('export/xlsx/',  exportviews.export_retail_past_policy_xlsx, name='export_xlsx_retail_past'),
    path('export/pdf/',  exportviews.export_retail_past_policy_pdf, name='export_pdf_retail_past'),


    path('Enq-followup/csv/', exportviews.export_followup_csv, name='export_followup_csvs'),
    path('Enq-followup/excel/', exportviews.export_followup_excel, name='export_followup_excels'),
    path('Enq-followup/pdf/', exportviews.export_followup_pdf, name='export_followup_pdfs'),


    path('export-followup-csv/',  exportviews.export_retail_followup_csv, name='export_ret_followup_csv'),
    path('export-followup-xlsx/',  exportviews.export_retail_followup_xlsx, name='export_ret_followup_xlsx'),
    path('export-followup-pdf/',  exportviews.export_retail_followup_pdf, name='export_ret_followup_pdf'),

    path('upload-excel/', views.upload_excel, name='upload_excel'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
