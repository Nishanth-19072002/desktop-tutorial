from django.urls import path
from . import views

urlpatterns = [
    path('',views.showAdminPanel,name="showAdminPanel"),

    # add module, sub module
    path('add-module',views.addModule,name="addModule"),
    path('add-submodule',views.addSubModule,name="addSubModule"),

    # delete module, sub module
    path('delete-module',views.deleteModule,name="deleteModule"),
    path('delete-submodule',views.deleteSubModule,name="deleteSubModule"),

    # retrieve all modules, submodules
    path('retrieveModules',views.retrieveModules,name="retieveModules"),
    path('retrieveAllSubModules',views.retrieveAllSubModules,name="retrieveAllSubModules"),

    # retrieve submodules based on module id
    path('retrieveSubModules',views.retriveSubModules,name="retrieveSubModules"),

    # save Logic Block Publish
    # path('saveFunctionBlockRecord',views.saveFunctionBlockRecord,name="saveFunctionBlockData"),
    # path('removeFunctionBlockRecod',views.removeFunctionBlockRecod,name="removeFunctionBlockData"),

    # save logic block awating (draft)
    path("save_logic_block_details",views.save_logic_block_details,name="save_logic_block_details"),
    path("retrieve_logic_blocks",views.retrieve_logic_blocks,name="retrieve_logic_blocks"),
    path("remove_logic_block",views.remove_logic_block,name="remove_logic_block"),

    # publish Block
    path("<int:block_id>/publish_block",views.publish_block,name="publish_block"),

    # Logic Blocks inputs and ui 
    path("<int:block_id>/get_block_user_inputs_ui",views.get_block_user_inputs_ui,name="get_block_user_inputs_ui"),
    path("<int:block_id>/LB_inputs",views.LB_inputs,name="LB_inputs"),
    path("<int:block_id>/put_design_params",views.put_design_params,name="put_design_params"),
    path("<int:block_id>/put_preformance_params",views.put_preformance_params,name="put_preformance_params"),
    path("<int:block_id>/put_lifing_params",views.put_lifing_params,name="put_lifing_params"),
    path("<int:block_id>/put_prognostic_params",views.put_prognostic_params,name="put_prognostic_params"),

    path("<int:block_id>/delete_design_input",views.delete_design_input,name="delete_design_input"),
    path("<int:block_id>/delete_performance_input",views.delete_performance_input,name="delete_performance_input"),
    path("<int:block_id>/delete_lifing_input",views.delete_lifing_input,name="delete_lifing_input"),
    path("<int:block_id>/delete_prognostics_input",views.delete_prognostics_input,name="delete_prognostics_input"),

    path("<int:block_id>/get_edit_block_user_ui",views.get_edit_block_user_ui,name="get_edit_block_user_ui"),
    path("<int:block_id>/edit_LB_inputs",views.edit_LB_inputs,name="edit_LB_inputs"),
    path("<int:block_id>/get_design_params",views.get_design_params,name="get_design_params"),
    path("<int:block_id>/get_performance_params",views.get_performance_params,name="get_performance_params"),
    path("<int:block_id>/get_lifing_params",views.get_lifing_params,name="get_lifing_params"),
    path("<int:block_id>/get_prognostic_params",views.get_prognostic_params,name="get_prognostic_params"),

    path("<int:block_id>/put_edited_design_params",views.put_edited_design_params,name="put_edited_params"),
    path("<int:block_id>/put_edited_performance_params",views.put_edited_performance_params,name="put_edited_performance_params"),
    path("<int:block_id>/put_edited_lifing_params",views.put_edited_lifing_params,name="put_edited_lifing_params"),
    path("<int:block_id>/put_edited_prognostic_params",views.put_edited_prognostic_params,name="put_edited_prognostic_params"),

    # logic blocks code and ui
    path("<int:block_id>/get_code_editor_ui",views.get_code_editor_ui,name="get_code_editor_ui"),
    path("<int:block_id>/LB-code-editor",views.LB_code_editor,name="LB-code-editor"),
    path("<int:block_id>/put_LB_design_Code",views.put_LB_Design_Code,name="put_LB_Design_Code"),
    path("<int:block_id>/put_LB_performance_Code",views.put_LB_Performance_Code,name="put_LB_Performance_Code"),
    path("<int:block_id>/put_LB_lifing_Code",views.put_LB_Lifing_Code,name="put_LB_Lifing_Code"),
    path("<int:block_id>/put_LB_prognostic_Code",views.put_LB_Prognostic_Code,name="put_LB_PrognosticCode"),

    path("<int:block_id>/get_edit_block_code_editor_ui",views.get_edit_block_code_editor_ui,name="get_edit_block_code_editor_ui"),
    path("<int:block_id>/LB-edit-code-CodeEditor",views.LB_edit_code_editor,name="LB-edit-code-editor"),
    path("<int:block_id>/get_design_code",views.get_design_code,name='get_design_code'),
    path("<int:block_id>/get_performance_code",views.get_performance_code,name='get_performance_code'),
    path("<int:block_id>/get_lifing_code",views.get_lifing_code,name='get_lifing_code'),
    path("<int:block_id>/get_prognostic_code",views.get_prognostic_code,name='get_prognostic_code'),

    path("<int:block_id>/put_design_edited_code",views.put_design_edited_code,name="put_design_edited_code"),
    path("<int:block_id>/put_performance_edited_code",views.put_performance_edited_code,name="put_performance_edited_code"),
    path("<int:block_id>/put_lifing_edited_code",views.put_lifing_edited_code,name="put_lifing_edited_code"),
    path("<int:block_id>/put_prognostic_edited_code",views.put_prognostic_edited_code,name="put_prognostic_edited_code"),

    # logic block outputs and ui
    path("<int:block_id>/get_block_user_outputs_ui",views.get_block_user_outputs_ui,name="get_block_user_outputs_ui"),
    path("<int:block_id>/LB_outputs",views.LB_outputs,name="LB_outputs"),
    path("<int:block_id>/put_design_out_params",views.put_design_out_params,name="put_design_out_params"),
    path("<int:block_id>/put_preformance_out_params",views.put_preformance_out_params,name="put_preformance_out_params"),
    path("<int:block_id>/put_lifing_out_params",views.put_lifing_out_params,name="put_lifing_out_params"),
    path("<int:block_id>/put_prognostic_out_params",views.put_prognostic_out_params,name="put_prognostic_out_params"),

    path("<int:block_id>/delete_design_output",views.delete_design_output,name="delete_design_output"),
    path("<int:block_id>/delete_performance_output",views.delete_performance_output,name="delete_performance_output"),
    path("<int:block_id>/delete_lifing_output",views.delete_lifing_output,name="delete_lifing_output"),
    path("<int:block_id>/delete_prognostics_output",views.delete_prognostics_output,name="delete_prognostics_output"),

    path("<int:block_id>/get_edit_block_output_user_ui",views.get_edit_block_output_user_ui,name="get_edit_block_output_user_ui"),
    path("<int:block_id>/edit_LB_outputs",views.edit_LB_outputs,name="edit_LB_outputs"),
    path("<int:block_id>/get_design_output_params",views.get_design_output_params,name="get_design_output_params"),
    path("<int:block_id>/get_performance_output_params",views.get_performance_output_params,name="get_performance_output_params"),
    path("<int:block_id>/get_lifing_output_params",views.get_lifing_output_params,name="get_lifing_output_params"),
    path("<int:block_id>/get_prognostic_output_params",views.get_prognostic_output_params,name="get_prognostic_output_params"),

    path("<int:block_id>/put_edited_design_output",views.put_edited_design_output,name="put_edited_output"),
    path("<int:block_id>/put_edited_performance_output",views.put_edited_performance_output,name="put_edited_performance_output"),
    path("<int:block_id>/put_edited_lifing_output",views.put_edited_lifing_output,name="put_edited_lifing_output"),
    path("<int:block_id>/put_edited_prognostic_output",views.put_edited_prognostic_output,name="put_edited_prognostic_output"),

]