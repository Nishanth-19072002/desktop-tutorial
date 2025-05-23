from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    
    path('index',views.index,name="index"),
    path('',views.landingpage,name="landpage"),

    # network and details
    # path('save_network_details',views.save_network_details,name="save_network_details"),
    path('save_network_current_state',views.save_network_current_state,name='save_network_current_state'),
    path('get_network_current_state',views.get_network_current_state,name='get_network_current_state'),

    # user simulate page
    path('simulate',views.home,name="homePage"),

    # function block clone and details
    path('put_function_block_clone',views.put_function_block_clone,name="put_function_block_clone"),
    path('put_function_block_clone_recon',views.put_function_block_clone_recon,name="put_function_block_clone_recon"),
    path('delete_function_block_clone',views.delete_function_block_clone,name="delete_function_block_clone"),

    # function block connection and details
    path("make_block_connection",views.make_block_connection,name="make_block_connection"),
    path("make_block_connection_reconst",views.make_block_connection_reconst,name="make_block_connection_reconst"),
    path("remove_function_block_connection",views.remove_function_block_connection,name="remove_function_block_connection"),
    path("get_dest_block_num_connections",views.get_dest_block_num_connections,name="get_dest_block_num_connections"),
    path("get_conncetion_existence",views.get_conncetion_existence,name="get_conncetion_existence"),
    

    #user input value related
    path("<str:true_block_id>/<str:clone_block_id>/go_back_to_home",views.go_back_to_home,name="go_back_to_home"),
    path("<str:true_block_id>/<str:clone_block_id>/get_user_inputs_value_url",views.get_user_inputs_value_url,name="get_user_inputs_value_url"),
    path("<str:true_block_id>/<str:clone_block_id>/block_user_input_value",views.block_user_input_value,name="block_user_input_value"),
    path("<str:true_block_id>/<str:clone_block_id>/get_block_inputs_populate",views.get_block_inputs_populate,name="get_block_inputs_populate"),
    path("<str:true_block_id>/<str:clone_block_id>/get_block_initial_inputs_populate",views.get_block_initial_inputs_populate,name="get_block_initial_inputs_populate"),
    path("<str:true_block_id>/<str:clone_block_id>/get_user_selected_excel_columns",views.get_user_selected_excel_columns,name="get_user_selected_excel_columns"),
    path("<str:true_block_id>/<str:clone_block_id>/get_network_excel_uploads",views.get_network_excel_uploads,name="get_network_excel_uploads"),
    path("<str:true_block_id>/<str:clone_block_id>/get_user_selected_excel_columns",views.get_user_selected_excel_columns,name="get_user_selected_excel_columns"),
    path("<str:true_block_id>/<str:clone_block_id>/get_function_block_dependencies",views.get_function_block_dependencies,name="get_function_block_dependencies"),
    path("<str:true_block_id>/<str:clone_block_id>/get_blocks_outputs",views.get_blocks_outputs,name="get_blocks_outputs"),
    path("<str:true_block_id>/<str:clone_block_id>/put_block_input_values",views.put_block_input_values,name="put_block_input_values"),
    path("<str:true_block_id>/<str:clone_block_id>/put_block_initial_input_values",views.put_block_initial_input_values,name="put_block_initial_input_values"),
    
    path("put_function_block_name",views.put_function_block_name,name="put_function_block_name"),

    # user network save and reconst related main network
    path("save_user_network",views.save_user_network,name="save_user_network"),
    path("get_user_networks",views.get_user_networks,name="get_user_networks"),

    path("get_user_selected_network",views.get_user_selected_network,name="get_user_selected_network"),

    path("load_user_inputs_to_folder",views.load_user_inputs_to_folder,name="load_user_inputs_to_folder"),
    

    path('clear_all',views.clear_all,name="clear_all"),
    # path('get_function_block_dependencies',views.get_function_block_dependencies,name="get_function_block_dependencies"),

    # path('save_block_input_to_file',views.save_block_input_to_file,name='save_block_input_to_file'),
    path('getTreeData',views.get_tree_data,name="getTreeData"),
    path('run_simulation',views.run_simulation,name="runSimulation"),
    # path('makeblockconnection',views.make_block_connection,name="makeblockconnection"),
    # path('removeblockconnection',views.remove_block_connection,name="removeblockconnection"),
    # path('saveNetwork',views.save_network,name="saveNetwork"),
    
    path("save_network_excel_csv",views.save_network_excel_csv,name="save_network_excel_csv"),
    path("get_network_excel_uploads",views.get_network_excel_uploads,name="get_network_excel_uploads"),

    # not in use
    # path('addDisplayRecord',views.add_display_record,name="addDisplayRecord"),
    # path('removeDisplayBlockRecord',views.delete_display_record,name="removeblockconnection"),
    # path('getAllDisplayIdValuePair',views.get_all_display_id_value_pair,name="getAllDisplayBlock"),
    # path("getFuncIdResPair",views.get_all_function_id_res_pair,name="getFuncIdResPair"),
    # path('getdependencies',views.get_dependency,name="getDependencies"),
    # path('getparamvalue',views.get_param_value,name="getparmavalue"),
    # path("retrive_network_files",views.retrive_network_files,name="retrive_network_files"),
    # path("get_columns_node_selected_file",views.get_columns_node_selected_file,name="get_columns_node_selected_file"),



    # developer login path
    path('login/developer', views.developer_login_view, name='developer_login'),
    path('login/user', views.User_login_view, name='user_login'),
    path('login/admin', views.Admin_login_view, name='admin_login'),
    path('developer/dashboard', views.developer_dashboard, name='developer_dashboard'),     
    path('Groups/', views.create_groups, name='groups'),     
    path('Users/', views.create_user, name='userss'),     
    path('logout/', LogoutView.as_view(next_page='landpage'), name='logout'),
    path("networks/<int:user_id>/", views.get_user_networks_forsharing, name="get_user_networks_sharing"),
    # path('share-network/', views.share_network, name='share_network'),
    path('change-group/<int:user_id>/', views.change_user_group, name='change_user_group'),
    path('project/', views.project_selection, name='project_selection'),
    path('project-simulate/<int:user_id>/', views.simulate_project, name='simulate_project'),
    path('project-simulate1/<int:user_id>/', views.simulate_existing_project, name='simulate_existing_project'),

    path('set-visibility/<int:user_id>/', views.set_user_visibility, name='set_user_visibility'),

    # sharing project #
    path('share_project/', views.share_project, name='share_project'),
    path('project-structure/<int:user_id>/', views.get_user_project_structure, name='get_user_project_structure'),
    path("get-all-users/", views.get_all_users, name="get_all_users"),
    path("get-user-projects/<int:user_id>/", views.get_user_projects, name="get_user_projects"),
    path("push-network/", views.push_network, name="push_network"),

    path('delete-project/<int:user_id>/<int:project_id>/', views.delete_project, name='delete_project'),
    path("delete-network/<int:user_id>/<int:project_id>/<str:category_type>/<str:net_type>/<str:file_name>/", views.delete_network_file),


]



 