from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse,HttpRequest
from django.conf import settings
# from django.contrib.auth.models import User
import json
from .models import *
import ast
from .typecaste import TypeCasting
import re
from django.db import transaction
from fluidsim.exeOrder import get_execution_order
from fluidsim.block_import_inputs import get_inputs_block
from fluidsim.blocks_initial_import_inputs import get_initial_inputs_block
from fluidsim.get_block_outputs import *
import importlib.util
from fluidsim.Exceptions import NoBlockFoundError,BlockDataError
import os
import shutil
import pandas as pd
import shutil
import time

# admin page and superuser related views.
def showAdminPanel(request):
    return render(request,'admin_panel.html')

#landing page 
def landingpage(request):
    return render(request,'landingpage.html')

# home page and user related content views
def index(request):
    return render(request,'index.html')

def home(request, user_id):
    project_id = request.GET.get('project_id')
    category_type = request.GET.get('category_type')
    net_type = request.GET.get('net_type')

    context = {
        'project_id': project_id,
        'category_type': category_type,
        'net_type': net_type,
        'user_id': user_id,
    }
    return render(request, 'home.html', context)

# def save_network_details(request):
#     if request.method == 'POST':
#         networkName = request.POST.get("network_name")
#         networkType = request.POST.get("network_type")
#         try:
#             user_instance = UserNetwork(
#                 user=request.user,
#                 network_name=networkName,
#                 network_type=networkType
#             )
#             user_instance.save()

#             user_id = request.user.id

#             return redirect(f"/{user_id}/simulate")

#         except Exception as e:
#             return redirect("index")
#     else:
#         return JsonResponse({'status': 'error', 'message': 'Invalid request'})

    
# def save_network_current_state(request,user_id):
#     if(request.method == 'POST'):
#         username = request.user.username
#         user_id = str(request.user.id)
#         networkState = json.loads(request.body)['state']
#         try:
#             if(os.path.exists(os.path.join(settings.NETWORK_CURRENT_STATE,   user_id,f"{str(user_id)}"))):
#                 with open(os.path.join(settings.NETWORK_CURRENT_STATE,  user_id,f"{str(user_id)}","current_network_state.json"),'w') as wp:
#                     json.dump(networkState,wp,indent=4)
#                 return JsonResponse({"status":"success","message":"saved Current State."}) 
#             else:
#                 os.makedirs(os.path.join(settings.NETWORK_CURRENT_STATE,  user_id,f"{str(user_id)}"),exist_ok=True)
#                 with open(os.path.join(settings.NETWORK_CURRENT_STATE,  user_id,f"{str(user_id)}","current_network_state.json"),'w') as wp:
#                     json.dump(networkState,wp,indent=4)
#                 return JsonResponse({"status":"success","message":"saved Current State."}) 
            
#         except Exception as e:
#             print(e)
#             return JsonResponse({"status":"error","message":f"{str(e)}"}) 
#     else:
#         return JsonResponse({'status':'error','message':'Invalid request'})
    
# def get_network_current_state(request, user_id):
#     if request.method == 'GET':
#         username = request.user.username
#         user_id = str(request.user.id)
#         print("*******enter******")

#         # Construct the file path
#         file_path = os.path.join(settings.NETWORK_CURRENT_STATE,   user_id, f"{str(user_id)}", "current_network_state.json")
        
#         try:
#             # Check if the file exists before attempting to open it
#             if os.path.exists(file_path):
#                 with open(file_path, 'r') as rp:
#                     networkCurrentState = json.load(rp)
#                 print(networkCurrentState)
#                 return JsonResponse({'status': 'success', 'state': networkCurrentState})
#             else:
#                 print(f"File does not exist: {file_path}")
#                 return JsonResponse({'status': 'success', 'state': None})

#         except Exception as e:
#             print(e)
#             return JsonResponse({'status': 'error', 'message': f"{str(e)}"})
#     else:
#         return JsonResponse({'status': 'error', 'message': 'Invalid request'})

    
def save_network_current_state(request,user_id):
    if(request.method == 'POST'):
        networkState = json.loads(request.body)['state']
        try:
            if(os.path.exists(os.path.join(settings.NETWORK_CURRENT_STATE,f"{str(user_id)}"))):
                with open(os.path.join(settings.NETWORK_CURRENT_STATE,f"{str(user_id)}","current_network_state.json"),'w') as wp:
                    json.dump(networkState,wp,indent=4)
                return JsonResponse({"status":"success","message":"saved Current State."}) 
            else:
                os.makedirs(os.path.join(settings.NETWORK_CURRENT_STATE,f"{str(user_id)}"),exist_ok=True)
                with open(os.path.join(settings.NETWORK_CURRENT_STATE,f"{str(user_id)}","current_network_state.json"),'w') as wp:
                    json.dump(networkState,wp,indent=4)
                return JsonResponse({"status":"success","message":"saved Current State."}) 
            
        except Exception as e:
            print(e)
            return JsonResponse({"status":"error","message":f"{str(e)}"}) 
    else:
        return JsonResponse({'status':'error','message':'Invalid request'})

def get_network_current_state(request,user_id):
    if(request.method == 'GET'):
        print("*******enter******")
        try:
            networkCurrentState = None
            if(os.path.join(settings.NETWORK_CURRENT_STATE,f"{str(user_id)}","current_network_state.json")):
                with open(os.path.join(settings.NETWORK_CURRENT_STATE,f"{str(user_id)}","current_network_state.json"),'r') as rp:
                    networkCurrentState = json.load(rp)
                print(networkCurrentState)
                return JsonResponse({'status':'success','state':networkCurrentState})
            else:
                return JsonResponse({'status':'success','state':None})
        except Exception as e:
            print(e)
            return JsonResponse({'status':'error','message':f"{str(e)}"})
    else:
        return JsonResponse({'status':'error','message':'Invalid request'})


    
def addModule(request):
    if(request.method=='POST'):
        try:
            module_name = request.POST.get('module_name')
            new_module = Modules(name=module_name)
            new_module.save()
            return redirect('/admin_panel')
        except:
            return JsonResponse({'status':'error','message':'module not added'})
    else:
        return JsonResponse({'status':'error','message':'Invalid request'})

def retrieveModules(request):
    if(request.method == 'GET'):
        modules = Modules.objects.all()
        # Prepare the module data as a list of dictionaries
        module_data = [
            {'id': module.id, 'name': module.name }
            for module in modules
        ]
        return JsonResponse({'modules':module_data})
    
def deleteModule(request):
    if(request.method == 'POST'):
        deleteModuleId = request.POST.get('module_id')
        deleteRecord = Modules.objects.get(id = deleteModuleId)
        deleteRecord.delete()
        return redirect('/admin_panel')

def addSubModule(request):
    if(request.method == 'POST'):
        try:
            moduleId = request.POST.get('module_id')
            submodule_name = request.POST.get('submodule_name')
            print(moduleId,submodule_name)
            new_submodule = SubModules(name=submodule_name,module_id=moduleId)
            new_submodule.save()
            return redirect('/admin_panel')
        except:
            return JsonResponse({'status':'error','message':'submodule not added'})

def retriveSubModules(request):
    if(request.method == 'POST'):
        try:
            data = json.loads(request.body)
            moduleid = data['id']
            submodules = SubModules.objects.filter(module_id = moduleid)
            submodules_data = [{'id':submodule.id,'name':submodule.name}
                for submodule in submodules
            ]
            return JsonResponse({'submodules':submodules_data})
        except:
            return JsonResponse({'status':'error','message':'failed to fetch submodules'})
    else:
        return JsonResponse({'status':'error','message':'Invalid request'})

def retrieveAllSubModules(request):
    if(request.method == 'GET'):
        allsubmodules = SubModules.objects.all()
        allsubmodules_data = [{'id':submodule.id ,'name':submodule.name}
            for submodule in allsubmodules
        ]
        return JsonResponse({'allsubmodules' : allsubmodules_data})
    
def deleteSubModule(request):
    if(request.method == 'POST'):
        toDeleteRecordId = request.POST.get('submodule_id')
        SubModules.objects.get(id = toDeleteRecordId).delete()
        return redirect('/admin_panel')

    
def save_network_excel_csv(request,user_id):
    if(request.method == 'POST'):
        files = request.FILES.getlist('files')
        networkInputFolder = os.path.join(settings.NETWORK_INPUT_FILES,f"{str(user_id)}")
        saved_files = [] 
        try:
            if(os.path.exists(networkInputFolder)):
                for file in files:
                    print(file)
                    networkInputFilePath = os.path.join(networkInputFolder,file.name)
                    with open(networkInputFilePath, 'wb+') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                    saved_files.append(file.name)
                return JsonResponse({
                    "status": "success",
                    "message": f"Successfully saved {len(saved_files)} files.",
                    "files": saved_files
                })
            else:
                os.makedirs(os.path.join(settings.NETWORK_INPUT_FILES,f"{str(user_id)}"),exist_ok=True)
                for file in files:
                    networkInputFilePath = os.path.join(networkInputFolder,file.name)
                    with open(networkInputFilePath, 'wb+') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                    saved_files.append(file.name)
                return JsonResponse({
                    "status": "success",
                    "message": f"Successfully saved {len(saved_files)} files.",
                    "files": saved_files
                })
        except Exception as e:
            print("Error saving files:", e)
            return JsonResponse({
                "status": "error",
                "message": "Failed to save files."
            }, status=500)
    else:
        return JsonResponse({'status':'error','message':'Invalid Request'})
    
# def retrive_network_files(request):
#     if(request.method == 'GET'):
#         try:
#             network_input_folder = "D:/Xpredictsoftware/simulationsoftware/fluidsim/network_input_files"
#             allowed_extensions = ('.csv','.xlsx')
#             files = [
#                 file for file in os.listdir(network_input_folder)
#                 if os.path.isfile(os.path.join(network_input_folder, file)) and file.endswith(allowed_extensions)
#             ]
#             return JsonResponse({'status':'success','message':'fetched network files',"files": files})
#         except Exception as e:
#             return JsonResponse({'status':'error','message':'failed to fetched network files'})
#     else:
#         return JsonResponse({'status':'error','message':'Invalid Request'})

# def get_columns_node_selected_file(request):
#     if(request.method == 'POST'):
#         value = json.loads(request.body)['value']
#         try:
#             network_input_file = f"D:/Xpredictsoftware/simulationsoftware/fluidsim/network_input_files/{value}"
#             if(os.path.exists(network_input_file)):
#                 if(value.endswith('.csv')):
#                     df = pd.read_csv(network_input_file)
#                 elif value.endswith(('.xls', '.xlsx')):
#                     df = pd.read_excel(network_input_file, engine='openpyxl')
#                 else:
#                     return JsonResponse({"status": "error", "message": "Unsupported file format"}, status=400)
                
#                 columns = df.columns.tolist()
#                 return JsonResponse({
#                 "status": "success",
#                 "columns": columns
#             })
#         except Exception as e:
#             print("Error processing file:", e)
#             return JsonResponse({"status": "error", "message": "Failed to process file"}, status=500)

#     else:
#         return JsonResponse({'status':'error','message':'Invalid Request'})
    
def get_network_excel_uploads(request,user_id,true_block_id,clone_block_id):
    if(request.method == 'GET'):
        try:
            network_input_folder = os.path.join(settings.NETWORK_INPUT_FILES,f"{str(user_id)}")
            if(os.path.exists(network_input_folder)):
                allowed_extensions = ('.csv','.xlsx')
                files = [
                    file for file in os.listdir(network_input_folder)
                    if os.path.isfile(os.path.join(network_input_folder, file)) and file.endswith(allowed_extensions)
                ]
                return JsonResponse({'status':'success','message':'fetched network files',"files": files})
            else:
                files=[]
                return JsonResponse({'status':'success','message':'fetched network files',"files": files})
        except Exception as e:
            print(e)
            return JsonResponse({'status':'error','message':'failed to fetched network files'})
    else:
        return JsonResponse({'status':'error','message':'Invalid Request'})

def get_user_selected_excel_columns(request,user_id,true_block_id,clone_block_id):
    if(request.method == 'POST'):
        value = json.loads(request.body)['excel_name']
        try:
            network_input_file = os.path.join(settings.NETWORK_INPUT_FILES,f"{str(user_id)}",f"{value}")
            if(os.path.exists(network_input_file)):
                if(value.endswith('.csv')):
                    df = pd.read_csv(network_input_file)
                elif value.endswith(('.xls', '.xlsx')):
                    df = pd.read_excel(network_input_file, engine='openpyxl')
                else:
                    return JsonResponse({"status": "error", "message": "Unsupported file format"}, status=400)
                
                columns = df.columns.tolist()
                return JsonResponse({
                "status": "success",
                "columns": columns
            })
        except Exception as e:
            print("Error processing file:", e)
            return JsonResponse({"status": "error", "message": "Failed to process file"}, status=500)
    else:
        return JsonResponse({'status':'error','message':'Invalid Request'})
    
def get_blocks_outputs(request,user_id,true_block_id,clone_block_id):
    if(request.method=='POST'):
        try:
            previousBlockId = json.loads(request.body)['previous_block_id']; 
        
            networkInstace = Network.objects.get(pk=user_id)
            networkType = networkInstace.network_type
           
            if(networkType == 'design'):
                outputs = []
                previousBlockInstance = functionBlockData.objects.get(pk=previousBlockId).true_LB_id
                
                designOutputInstances = LogicBlockDesignOutputs.objects.filter(LB_id = previousBlockInstance)
               
                for designOutputInstance in designOutputInstances:
                    outs = {
                        "id":designOutputInstance.pk,
                        "param_name":designOutputInstance.out_param_name,
                        "unit":designOutputInstance.unit
                    }
                    outputs.append(outs)
                return JsonResponse({"status":"success","outputs":outputs})
            elif(networkType == 'performance'):
                pass
            elif(networkType == 'lifing'):
                pass
            else:
                pass
        except Exception as e:
            print(e)
            return JsonResponse({"status":'error',"message":"no outputs found"})
    else:
        return JsonResponse({'status':'error','message':'Invalid Request'})
    
def put_block_input_values(request,user_id,true_block_id,clone_block_id):
    if(request.method == 'POST'):
        project_id = request.POST.get('project_id')
        category_type = request.POST.get('category_type')
        net_type = request.POST.get('net_type')

        print(f"esf",project_id)
        print(f"esf",category_type)
        print(f"esf",net_type)

        blocksIOroot = settings.BLOCK_IO
        inputs_values = json.loads(request.body)
        try:
            if(not os.path.exists(os.path.join(blocksIOroot,f"{str(user_id)}"))):
                os.makedirs(os.path.join(blocksIOroot,f"{str(user_id)}",f"{str(true_block_id)}"),exist_ok=True)
                IOJsonFile = os.path.join(blocksIOroot,f"{str(user_id)}",f"{str(true_block_id)}",f"{str(clone_block_id)}.json")
                with open(IOJsonFile,'w') as wp:
                    json.dump(inputs_values,wp,indent=4)
            else:
                if(not os.path.exists(os.path.join(blocksIOroot,f"{str(user_id)}",f"{str(true_block_id)}"))):
                    os.makedirs(os.path.join(blocksIOroot,f"{str(user_id)}",f"{str(true_block_id)}"),exist_ok=True)
                    IOJsonFile = os.path.join(blocksIOroot,f"{str(user_id)}",f"{str(true_block_id)}",f"{str(clone_block_id)}.json")
                    with open(IOJsonFile,'w') as wp:
                        json.dump(inputs_values,wp,indent=4)
                else:
                    IOJsonFile = os.path.join(blocksIOroot,f"{str(user_id)}",f"{str(true_block_id)}",f"{str(clone_block_id)}.json")
                    with open(IOJsonFile,'w') as wp:
                        json.dump(inputs_values,wp,indent=4)
            return JsonResponse({"status":"success","message":"input values saved."})
        except Exception as e:
            print(e)

    else:
        return JsonResponse({'status':'error','message':'Invalid Request'})
    
def put_block_initial_input_values(request,user_id,true_block_id,clone_block_id):
    if(request.method == 'POST'):
        blocksIOroot = settings.CIRCULAR_BLOCK_DEPENDENCY_DATA
        inputs_values = json.loads(request.body)
        try:
            if(not os.path.exists(os.path.join(blocksIOroot,f"{str(user_id)}"))):
                os.makedirs(os.path.join(blocksIOroot,f"{str(user_id)}",f"{str(true_block_id)}"),exist_ok=True)
                IOJsonFile = os.path.join(blocksIOroot,f"{str(user_id)}",f"{str(true_block_id)}",f"{str(clone_block_id)}.json")
                with open(IOJsonFile,'w') as wp:
                    json.dump(inputs_values,wp,indent=4)
            else:
                if(not os.path.exists(os.path.join(blocksIOroot,f"{str(user_id)}",f"{str(true_block_id)}"))):
                    os.makedirs(os.path.join(blocksIOroot,f"{str(user_id)}",f"{str(true_block_id)}"),exist_ok=True)
                    IOJsonFile = os.path.join(blocksIOroot,f"{str(user_id)}",f"{str(true_block_id)}",f"{str(clone_block_id)}.json")
                    with open(IOJsonFile,'w') as wp:
                        json.dump(inputs_values,wp,indent=4)
                else:
                    IOJsonFile = os.path.join(blocksIOroot,f"{str(user_id)}",f"{str(true_block_id)}",f"{str(clone_block_id)}.json")
                    with open(IOJsonFile,'w') as wp:
                        json.dump(inputs_values,wp,indent=4)
            return JsonResponse({"status":"success","message":"input values saved."})
        except Exception as e:
            print(e)

    else:
        return JsonResponse({'status':'error','message':'Invalid Request'})
    


from django.contrib.auth.decorators import login_required

@login_required
def get_tree_data(request, user_id):
    if request.method == 'GET':
        try:
            user = request.user

            # Fetch only the modules the user has access to
            allowed_modules = UserModuleAccess.objects.filter(user=user).values_list('module_id', flat=True)
            modules = Modules.objects.filter(id__in=allowed_modules)

            # Fetch only the submodules the user has access to
            allowed_submodules = UserSubmoduleAccess.objects.filter(user=user).values_list('submodule_id', flat=True)
            submodules = SubModules.objects.filter(id__in=allowed_submodules)

            data = []
            for module in modules:
                module_data = {
                    'id': module.id,
                    'name': module.name,
                    'submodules': []
                }

                # Filter submodules based on user access
                for submodule in module.submodules.all():
                    if submodule.id in allowed_submodules:
                        submodule_data = {
                            'id': submodule.id,
                            'name': submodule.name,
                            'logic_blocks': [
                                {
                                    'id': logic_block.id,
                                    'name': logic_block.name,
                                    'blocktype': logic_block.block_type,
                                    'mode': logic_block.mode,
                                    'publish': logic_block.publish
                                }
                                for logic_block in submodule.logic_blocks.filter(publish=True)
                            ]
                        }
                        module_data['submodules'].append(submodule_data)

                # Only append modules with submodules
                if module_data['submodules']:
                    data.append(module_data)

            return JsonResponse(data, safe=False)

        except Exception as e:
            print(e)
            return JsonResponse({'status': 'error', 'message': 'Failed to fetch filtered modules and submodules.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    


# @transaction.atomic
def put_function_block_clone(request,user_id):
    if(request.method == 'POST'):
        try:
            data = json.loads(request.body)

            id = data['id']
            true_id = data["true_id"]

            trueLBInstance = LogicBlocks.objects.get(pk=true_id)
            networkInstance = Network.objects.get(pk=user_id)

            functionBlockInstance = functionBlockData(id=id,true_LB_id=trueLBInstance,network_id = networkInstance)
            functionBlockInstance.save()

            return JsonResponse({'status': 'success','message': 'Record inserted successfully'})
        except Exception as e:
            print(e)
            return JsonResponse({'stauts': 'error','message':'record not inserted'}, status=404)
    else:
        return JsonResponse({'status':'error','message':'Invalid request method'},status=400)
    
def put_function_block_clone_recon(request,user_id):
    if(request.method == 'POST'):
        id = json.loads(request.body)['id']
        true_LB_id = json.loads(request.body)['true_LB_id']
        proxy_name = json.loads(request.body)['proxy_name']
        try:
            networkInstance = Network.objects.get(pk=user_id)
            trueBlockInstance = LogicBlocks.objects.get(pk=true_LB_id)

            functionBlockData(pk=id,true_LB_id=trueBlockInstance,network_id=networkInstance,proxy_name=proxy_name).save()

            return JsonResponse({'status': 'success','message': 'Record inserted successfully'})

        except Exception as e:
            print(e)
            return JsonResponse({'status':"error","message":"failed to insert Record"})
    else:
        return JsonResponse({'status':'error','message':'Invalid request method'},status=400)

def put_function_block_name(request,user_id):
    if(request.method == 'POST'):
        try:
            block_name = json.loads(request.body)['user_block_name']
            id = json.loads(request.body)['clone_id']

            functionInsatnce = functionBlockData.objects.get(id=id,network_id=user_id)
            functionInsatnce.proxy_name = block_name
            functionInsatnce.save()

            return JsonResponse({'status': 'success','message': 'Block Name added'})
        except Exception as e:
            print(e)
            return JsonResponse({'stauts': 'error','message':'record not inserted'}, status=404)
    else:
        return JsonResponse({'status':'error','message':'Invalid request method'},status=400)
    
def delete_function_block_clone(request,user_id):
    if(request.method == 'POST'):
        try:
            data = json.loads(request.body)
            id = data['id']

            networkInstance = Network.objects.get(pk=user_id)
            functionBlockInstance = functionBlockData.objects.get(id = id,network_id = networkInstance)
            true_id = functionBlockInstance.true_LB_id.pk
            deleted_connections = list(Connections.objects.filter(source=functionBlockInstance) | Connections.objects.filter(destination=functionBlockInstance))
            deleted_connections_id = [id.pk for id in deleted_connections]
            
            functionBlockInstance.delete()
            if(os.path.exists(os.path.join(settings.BLOCK_IO,f"{str(user_id)}",f"{str(true_id)}",f"{str(id)}.json"))):
                os.remove(os.path.join(settings.BLOCK_IO,f"{str(user_id)}",f"{str(true_id)}",f"{str(id)}.json"))
                if(os.path.exists(os.path.join(settings.CIRCULAR_BLOCK_DEPENDENCY_DATA,f"{str(user_id)}",f"{str(true_id)}",f"{str(id)}.json"))):
                    os.remove(os.path.join(settings.CIRCULAR_BLOCK_DEPENDENCY_DATA,f"{str(user_id)}",f"{str(true_id)}",f"{str(id)}.json"))
                    return JsonResponse({'status': 'success', 'message': 'Records deleted successfully, Block IO removed Successfully, initals records','connection_ids':deleted_connections_id})
                return JsonResponse({'status': 'success', 'message': 'Records deleted successfully and Block IO removed Successfully','connection_ids':deleted_connections_id})
            else:
                return JsonResponse({'status': 'success', 'message': 'Records deleted successfully','connection_ids':deleted_connections_id})
        except functionBlockData.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Records not found'}, status=404)
        except Exception as e:
            print(e)
            return JsonResponse({'status': 'error', 'message': 'not able to delete blockIO'}, status=404)
    else:
        return JsonResponse({'status':'error','message':'Invalid request method'},status=400)
    
# def save_user_network(request,user_id):
#     if(request.method == 'POST'):
#         user_id = str(request.user.id) 
#         workspacePostionState = json.loads(request.body)['workspacePostionState']
#         fileName = json.loads(request.body)['myfilename']

#         # save network
#         if(not os.path.exists(os.path.join(settings.USER_NETWORKS,  user_id, f"{str(user_id)}"))):
#             os.makedirs(os.path.join(settings.USER_NETWORKS, user_id,f"{str(user_id)}"),exist_ok=True)
            
#             if(not os.path.exists(os.path.join(settings.USER_NETWORKS,  user_id,f"{str(user_id)}",f"{str(fileName)}"))):
#                 os.makedirs(os.path.join(settings.USER_NETWORKS,  user_id,f"{str(user_id)}",f"{str(fileName)}"),exist_ok=True)
                
#                 userSaveFile = os.path.join(settings.USER_NETWORKS,  user_id,f"{str(user_id)}",f"{str(fileName)}","network.json")
#                 with open(userSaveFile,"w") as wp:
#                     json.dump(workspacePostionState,wp,indent=4)

#                 saved_network_inputs_values = save_user_network_inputs_values(request,user_id,fileName)
#                 if(saved_network_inputs_values):
#                     return JsonResponse({"status":'success',"message":'network and its related block IO saved successfully'})
#                 else:
#                     return JsonResponse({"status":'success',"message":'network and saved successfully'})
#             else:
#                 userSaveFile = os.path.join(settings.USER_NETWORKS,  user_id,f"{str(user_id)}",f"{str(fileName)}","network.json")
#                 with open(userSaveFile,"w") as wp:
#                     json.dump(workspacePostionState,wp,indent=4)

#                 saved_network_inputs_values = save_user_network_inputs_values(request,user_id,fileName)
#                 if(saved_network_inputs_values):
#                     return JsonResponse({"status":'success',"message":'network and its related block IO saved successfully'})
#                 else:
#                     return JsonResponse({"status":'success',"message":'network and saved successfully'})
               
            
#         else:
#             if(not os.path.exists(os.path.join(settings.USER_NETWORKS,  user_id,f"{str(user_id)}",f"{str(fileName)}"))):
#                 os.makedirs(os.path.join(settings.USER_NETWORKS,  user_id,f"{str(user_id)}",f"{str(fileName)}"),exist_ok=True)

#                 userSaveFile = os.path.join(settings.USER_NETWORKS,  user_id,f"{str(user_id)}",f"{str(fileName)}","network.json")
#                 with open(userSaveFile,"w") as wp:
#                     json.dump(workspacePostionState,wp,indent=4)

#                 saved_network_inputs_values = save_user_network_inputs_values(request,user_id,fileName)
#                 if(saved_network_inputs_values):
#                     return JsonResponse({"status":'success',"message":'network and its related block IO saved successfully'})
#                 else:
#                     return JsonResponse({"status":'success',"message":'network and saved successfully'})

#             else:
#                 userSaveFile = os.path.join(settings.USER_NETWORKS,  user_id,f"{str(user_id)}",f"{str(fileName)}","network.json")
#                 with open(userSaveFile,"w") as wp:
#                     json.dump(workspacePostionState,wp,indent=4)

#                 saved_network_inputs_values = save_user_network_inputs_values(request,user_id,fileName)
#                 if(saved_network_inputs_values):
#                     return JsonResponse({"status":'success',"message":'network and its related block IO saved successfully'})
#                 else:
#                     return JsonResponse({"status":'success',"message":'network and saved successfully'})
            
#         # save network block inputs
#     else:
#         return JsonResponse({'status':'error','message':'Invalid request method'},status=400)

# def save_user_network(request, user_id):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)

#             workspacePostionState = data.get('workspacePostionState')
#             fileName = data.get('myfilename')
#             project_id = data.get('project_id')
#             category_type = data.get('category_type')
#             net_type = data.get('net_type')

#             # Check for required fields
#             if not all([workspacePostionState, fileName, project_id, category_type, net_type]):
#                 return JsonResponse({
#                     'status': 'error',
#                     'message': 'Missing one or more required parameters'
#                 }, status=400)

#             # Construct full directory path
#             base_path = os.path.join(
#                 settings.USER_NETWORKS,
#                 str(user_id),
#                 str(project_id),
#                 category_type,
#                 net_type,
#                 str(fileName)
#             )

#             # Ensure directory exists
#             os.makedirs(base_path, exist_ok=True)

#             # Save network.json
#             userSaveFile = os.path.join(base_path, "network.json")
#             with open(userSaveFile, "w") as wp:
#                 json.dump(workspacePostionState, wp, indent=4)

#             # Save block input values
#             saved_network_inputs_values = save_user_network_inputs_values(request, user_id, fileName)

#             if saved_network_inputs_values:
#                 return JsonResponse({
#                     "status": 'success',
#                     "message": 'Network and its related block IO saved successfully'
#                 })
#             else:
#                 return JsonResponse({
#                     "status": 'success',
#                     "message": 'Network saved successfully'
#                 })

#         except json.JSONDecodeError as e:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': f'Invalid JSON data: {str(e)}'
#             }, status=400)

#         except Exception as e:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': f'An error occurred: {str(e)}'
#             }, status=500)

#     else:
#         return JsonResponse({
#             'status': 'error',
#             'message': 'Invalid request method. Expected POST.'
#         }, status=400)

    
def save_user_network(request,user_id):
    if(request.method == 'POST'):
        data = json.loads(request.body)
        workspacePostionState = json.loads(request.body)['workspacePostionState']
        fileName = json.loads(request.body)['myfilename']
        project_id = data.get('project_id')
        category_type = data.get('category_type')
        net_type = data.get('net_type')

        # save network
        if(not os.path.exists(os.path.join(settings.USER_NETWORKS,f"{str(user_id)}",f"{str(project_id)}",f"{str(category_type)}",f"{str(net_type)}"))):
            os.makedirs(os.path.join(settings.USER_NETWORKS,f"{str(user_id)}",f"{str(project_id)}",f"{str(category_type)}",f"{str(net_type)}"),exist_ok=True)
            
            if(not os.path.exists(os.path.join(settings.USER_NETWORKS,f"{str(user_id)}",f"{str(project_id)}",f"{str(category_type)}",f"{str(net_type)}",f"{str(fileName)}"))):
                os.makedirs(os.path.join(settings.USER_NETWORKS,f"{str(user_id)}",f"{str(project_id)}",f"{str(category_type)}",f"{str(net_type)}",f"{str(fileName)}"),exist_ok=True)
                
                userSaveFile = os.path.join(settings.USER_NETWORKS,f"{str(user_id)}",f"{str(project_id)}",f"{str(category_type)}",f"{str(net_type)}",f"{str(fileName)}","network.json")
                with open(userSaveFile,"w") as wp:
                    json.dump(workspacePostionState,wp,indent=4)

                saved_network_inputs_values = save_user_network_inputs_values(request,user_id,project_id,category_type,net_type,fileName)
                if(saved_network_inputs_values):
                    return JsonResponse({"status":'success',"message":'network and its related block IO saved successfully'})
                else:
                    return JsonResponse({"status":'success',"message":'network and saved successfully'})
            else:
                userSaveFile = os.path.join(settings.USER_NETWORKS,f"{str(user_id)}",f"{str(project_id)}",f"{str(category_type)}",f"{str(net_type)}",f"{str(fileName)}","network.json")
                with open(userSaveFile,"w") as wp:
                    json.dump(workspacePostionState,wp,indent=4)

                saved_network_inputs_values = save_user_network_inputs_values(request,user_id,project_id,category_type,net_type,fileName)
                if(saved_network_inputs_values):
                    return JsonResponse({"status":'success',"message":'network and its related block IO saved successfully'})
                else:
                    return JsonResponse({"status":'success',"message":'network and saved successfully'})
               
            
        else:
            if(not os.path.exists(os.path.join(settings.USER_NETWORKS,f"{str(user_id)}",f"{str(project_id)}",f"{str(category_type)}",f"{str(net_type)}",f"{str(fileName)}"))):
                os.makedirs(os.path.join(settings.USER_NETWORKS,f"{str(user_id)}",f"{str(project_id)}",f"{str(category_type)}",f"{str(net_type)}",f"{str(fileName)}"),exist_ok=True)

                userSaveFile = os.path.join(settings.USER_NETWORKS,f"{str(user_id)}",f"{str(project_id)}",f"{str(category_type)}",f"{str(net_type)}",f"{str(fileName)}","network.json")
                with open(userSaveFile,"w") as wp:
                    json.dump(workspacePostionState,wp,indent=4)

                saved_network_inputs_values = save_user_network_inputs_values(request,user_id,project_id,category_type,net_type,fileName)
                if(saved_network_inputs_values):
                    return JsonResponse({"status":'success',"message":'network and its related block IO saved successfully'})
                else:
                    return JsonResponse({"status":'success',"message":'network and saved successfully'})

            else:
                userSaveFile = os.path.join(settings.USER_NETWORKS,f"{str(user_id)}",f"{str(project_id)}",f"{str(category_type)}",f"{str(net_type)}",f"{str(fileName)}","network.json")
                with open(userSaveFile,"w") as wp:
                    json.dump(workspacePostionState,wp,indent=4)

                saved_network_inputs_values = save_user_network_inputs_values(request,user_id,project_id,category_type,net_type,fileName)
                if(saved_network_inputs_values):
                    return JsonResponse({"status":'success',"message":'network and its related block IO saved successfully'})
                else:
                    return JsonResponse({"status":'success',"message":'network and saved successfully'})
            
        # save network block inputs
    else:
        return JsonResponse({'status':'error','message':'Invalid request method'},status=400)

def save_user_network_inputs_values(request,user_id,project_id,category_type,net_type,fileName):
    try:
        if(os.path.exists(os.path.join(settings.USER_NETWORKS,f"{str(user_id)}",f"{str(project_id)}",f"{str(category_type)}",f"{str(net_type)}",f"{str(fileName)}"))):
            if(os.path.exists(os.path.join(settings.USER_NETWORKS,f"{str(user_id)}",f"{str(project_id)}",f"{str(category_type)}",f"{str(net_type)}",f"{str(fileName)}","inputs_values"))):
                shutil.rmtree(os.path.join(settings.USER_NETWORKS,f"{str(user_id)}",f"{str(project_id)}",f"{str(category_type)}",f"{str(net_type)}",f"{str(fileName)}","inputs_values"))
                if(os.path.exists(os.path.join(settings.BLOCK_IO,f"{str(user_id)}"))):
                    shutil.copytree(os.path.join(settings.BLOCK_IO,f"{str(user_id)}"),os.path.join(settings.USER_NETWORKS,f"{str(user_id)}",f"{str(project_id)}",f"{str(category_type)}",f"{str(net_type)},"f"{str(fileName)}","inputs_values"))
                    return True
                else:
                    return False
            else:
                if(os.path.exists(os.path.join(settings.BLOCK_IO,f"{str(user_id)}"))):
                    # os.makedirs(os.path.join(settings.USER_NETWORKS,f"{str(user_id)}",f"{str(fileName)}","inputs_values"),exist_ok=True)
                    shutil.copytree(os.path.join(settings.BLOCK_IO,f"{str(user_id)}"),os.path.join(settings.USER_NETWORKS,f"{str(user_id)}",f"{str(project_id)}",f"{str(category_type)}",f"{str(net_type)}",f"{str(fileName)}","inputs_values"))
                    return True
                else:
                    return False
        return False
    except Exception as e:
        print(e)


# def get_user_networks(request, user_id):
#     if request.method == "GET":
#         username = request.user.username
#         user_id = str(request.user.id)
#         network_path = os.path.join(settings.USER_NETWORKS,   user_id, f"{str(user_id)}")

#         if os.path.exists(network_path):


#             # List network folders inside the specific network directory
#             trueNetworkFolderNames = os.listdir(network_path)
#             if len(trueNetworkFolderNames) != 0:
#                 networkFolderNames = []
#                 for trueNetworkFolderName in trueNetworkFolderNames:
#                     # Assuming network folder names end with .json, so split to get the name
#                     name = trueNetworkFolderName.split(".json")[0]
#                     networkFolderNames.append(name)
#                 return JsonResponse({"status": "success", "network_files": networkFolderNames})
#             else:
#                 return JsonResponse({"status": "success", "message": "no networks found"})
#         else:
#             return JsonResponse({"status": "success", "error": "folder not found to fetch networks"})
#     else:
#         return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


# def get_user_selected_network(request, source_user_id):
#     if request.method == "POST":
#         body = json.loads(request.body)
#         network_name = body.get("network_name")
#         username = request.user.username
#         user_id = str(request.user.id)

#         network_path = os.path.join(
#             settings.USER_NETWORKS,
#             username,
#             user_id,
#             str(source_user_id),
#             network_name,
#             "network.json"
#         )

#         if os.path.exists(network_path):
#             with open(network_path, 'r') as f:
#                 data = json.load(f)
#             return JsonResponse({"status": "success", "network": data})
#         else:
#             return JsonResponse({"status": "error", "message": "Network file not found"})

#     return JsonResponse({"status": "error", "message": "Invalid request"})

    
# def get_user_networks(request,user_id):
#     if(request.method == "GET"):
#         user_id = str(request.user.id)
#         if(os.path.exists(os.path.join(settings.USER_NETWORKS,user_id,f"{str(user_id)}"))):
#             trueNetworkFolderNames = os.listdir(os.path.join(settings.USER_NETWORKS,user_id,f"{str(user_id)}"))
#             if(len(trueNetworkFolderNames)!=0):
#                 networkFolderNames = []
#                 for trueNetworkFolderName in trueNetworkFolderNames: 
#                     name = trueNetworkFolderName.split(".json")[0]
#                     networkFolderNames.append(name)
#                 return JsonResponse({"status":"success","network_files":networkFolderNames})
#             else:
#                 return JsonResponse({"status":"success",'message':"no networks found"})
#         else:
#             return JsonResponse({"status:success",'error',"folder not found to fetch networks"})
#     else:
#         return JsonResponse({'status':'error','message':'Invalid request method'},status=400)
    
# def get_user_selected_network(request,user_id):
#     if(request.method == "POST"):
#         user_id = str(request.user.id)
#         network_name = json.loads(request.body)['network_name']
#         if(os.path.exists(os.path.join(settings.USER_NETWORKS,user_id,f"{str(user_id)}",f"{network_name}","network.json"))):
#             network_file = os.path.join(settings.USER_NETWORKS,user_id,f"{str(user_id)}",f"{network_name}",f"network.json")

#             with open(network_file,"r") as rp:
#                 networkInstance = json.load(rp)
#             # load_inputs_values = load_user_inputs_to_folder(request,user_id,network_name)
#             # if(load_inputs_values):
#             #     return JsonResponse({"status":"success","message":"BLOCK IO loaded and also network","network":networkInstance,})
#             # else:
#             return JsonResponse({"status":"success","message":"network loaded","network":networkInstance,})
#         else:
#             return JsonResponse({"status":"error","message":"file not found"})
#     else:
#         return JsonResponse({'status':'error','message':'Invalid request method'},status=400)

    
import os
from django.conf import settings
from django.http import JsonResponse

def get_user_networks(request):
    user_id = request.user.id  # or get from session/auth
    if request.method == "GET":
        project_id = request.GET.get("project_id")
        category_type = request.GET.get("category_type")
        net_type = request.GET.get("network_type")

        print(f"Received params - project_id: {project_id}, category_type: {category_type}, net_type: {net_type}")

        if not all([project_id, category_type, net_type]):
            return JsonResponse({'status': 'error', 'message': 'Missing query parameters'}, status=400)

        # Base directory for this filter
        base_dir = os.path.join(
            settings.USER_NETWORKS,
            str(user_id),
            str(project_id),
            category_type,
            net_type
        )
        print(f"Looking in directory: {base_dir}")

        if os.path.exists(base_dir) and os.path.isdir(base_dir):
            network_files = []
            # Each entry in base_dir is a fileName directory or file
            for fileName in os.listdir(base_dir):
                file_path = os.path.join(base_dir, fileName)

                # Optionally check if this is a directory or file and if it contains 'network.json'
                network_json_path = os.path.join(file_path, 'network.json')

                if os.path.isfile(network_json_path):
                    network_files.append(fileName)

            if network_files:
                print(f"Found network files: {network_files}")
                return JsonResponse({"status": "success", "network_files": network_files})
            else:
                print("No network files found.")
                return JsonResponse({"status": "success", "message": "No networks found."})
        else:
            print(f"Directory not found: {base_dir}")
            return JsonResponse({"status": "error", "message": "Directory not found."})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)




def get_user_selected_network(request, user_id):
    if request.method == "POST":
        data = json.loads(request.body)
        network_name = data.get('network_name')

        # Traverse the expected directory structure
        user_dir = os.path.join(settings.USER_NETWORKS, str(user_id))

        for project_id in os.listdir(user_dir):
            project_path = os.path.join(user_dir, project_id)
            if not os.path.isdir(project_path):
                continue

            for category_type in os.listdir(project_path):
                category_path = os.path.join(project_path, category_type)
                if not os.path.isdir(category_path):
                    continue

                for net_type in os.listdir(category_path):
                    net_path = os.path.join(category_path, net_type)
                    if not os.path.isdir(net_path):
                        continue

                    for fileName in os.listdir(net_path):
                        if fileName == network_name:
                            network_file_path = os.path.join(net_path, fileName, "network.json")
                            if os.path.exists(network_file_path):
                                with open(network_file_path, "r") as rp:
                                    networkInstance = json.load(rp)
                                return JsonResponse({
                                    "status": "success",
                                    "message": "network loaded",
                                    "network": networkInstance,
                                })

        return JsonResponse({"status": "error", "message": "network not found"})

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    

    
    

# def load_user_inputs_to_folder(request,user_id):
#     if(request.method == 'POST'):
#         username = request.user.username
#         user_id = str(request.user.id)
#         network_name = json.loads(request.body)['network_name']
#         if(os.path.exists(os.path.join(settings.USER_NETWORKS,  user_id,f"{str(user_id)}",f"{network_name}",f"inputs_values"))):
#             shutil.copytree(src=os.path.join(settings.USER_NETWORKS,  user_id,f"{str(user_id)}",f"{str(network_name)}","inputs_values"),dst=os.path.join(settings.BLOCK_IO,f"{str(user_id)}"))
#             # for root,dirs,files in os.walk(os.path.join(settings.USER_NETWORKS,f"{str(user_id)}",f"{network_name}",f"inputs_values")):
#             #     print(os.path.realpath(root,(os.path.join(settings.BLOCK_IO,f"{str(user_id)}"))))
#             return JsonResponse({'status':'success','message':'added'})
#         else:
#             return JsonResponse({"status":"success","message":"no related inputs values"})
#     else:
#         return JsonResponse({'status':'error','message':'Invalid request method'},status=400)

    
def load_user_inputs_to_folder(request, user_id):
    if request.method == 'POST':
        try:
            network_name = json.loads(request.body)['network_name']
            user_dir = os.path.join(settings.USER_NETWORKS, str(user_id))

            # Traverse user -> project_id -> category_type -> net_type
            for project_id in os.listdir(user_dir):
                project_path = os.path.join(user_dir, project_id)
                if not os.path.isdir(project_path):
                    continue

                for category_type in os.listdir(project_path):
                    category_path = os.path.join(project_path, category_type)
                    if not os.path.isdir(category_path):
                        continue

                    for net_type in os.listdir(category_path):
                        net_path = os.path.join(category_path, net_type)
                        if not os.path.isdir(net_path):
                            continue

                        for item in os.listdir(net_path):
                            if item == network_name:
                                inputs_path = os.path.join(net_path, item, "inputs_values")
                                if os.path.exists(inputs_path):
                                    # ✅ Keep your original copytree destination
                                    shutil.copytree(
                                        src=inputs_path,
                                        dst=os.path.join(settings.BLOCK_IO, str(user_id)),
                                        dirs_exist_ok=True  # Optional: handle already existing dirs
                                    )
                                    return JsonResponse({'status': 'success', 'message': 'Inputs values added'})

            return JsonResponse({"status": "success", "message": "No related inputs values found"})

        except Exception as e:
            print(e)
            return JsonResponse({'status': 'error', 'message': 'Error during processing'}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

# def get_dependency(request):
#     try:
#         # Parse the block ID from the request
#         data = json.loads(request.body)
#         block_id = data['id']
        
#         # Find all blocks that `block_id` depends on
#         dependencies = Connections.objects.filter(destination_id=block_id)
        
#         if dependencies.exists():
#             dependency_data = []
            
#             for dependency in dependencies:
#                 # Get the source block information for each dependency
#                 source_block = functionBlockData.objects.get(id=dependency.source_id)
#                 dependency_data.append({
#                     "id": source_block.id,
#                 })
            
#             return JsonResponse({
#                 "status": "success",
#                 "dependencies": dependency_data  # Return all dependencies as a list
#             })
#         else:
#             return JsonResponse({"status": "success", "dependencies": None})  # No dependencies

#     except Exception as e:
#         return JsonResponse({"status": "error", "message": str(e)})


# def  get_all_function_id_res_pair(request):
#     if(request.method == 'GET'):
#         out = []
#         allFunctionBlock = functionBlockData.objects.all()
#         for function in allFunctionBlock:
#             print(function.res)
#             out.append({"id":function.id,"res":function.res})
#         return JsonResponse({"status":"success","message":"Function block Id and Result fetched successfully","data":out})
#     else:
#         return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def run_simulation(request, user_id):
    if(request.method == 'POST'):
        try:
            iter = json.loads(request.body)['iter']
            blocksExeOrder, cycles = get_execution_order(user_id)
            print(blocksExeOrder, cycles)

            if(len(blocksExeOrder) > 0):
                if(os.path.exists(os.path.join(settings.BLOCK_OUTS, f"{str(user_id)}"))):
                    shutil.rmtree(os.path.join(settings.BLOCK_OUTS, f"{str(user_id)}"))
                n = iter
                for iteration in range(0, n, 1):
                    for block in blocksExeOrder:
                        print("Execution Order: ", block)
                        print("Blocks in Cycle: ", cycles)
                        if(block in cycles):
                            print(f"***{block}***")
                            if(os.path.exists(os.path.join(settings.CIRCULAR_BLOCK_DEPENDENCY_DATA, f"{str(block.network_id.pk)}", f"{str(block.true_LB_id.pk)}", f"{str(block.pk)}.json"))):
                                params_values_initials = get_initial_inputs_block(block)
                                true_blocks_out_intials = {
                                    'blockId': block.pk,
                                    'blockProxyName': block.proxy_name,
                                    'outputs': []
                                }
                                if(params_values_initials):
                                    if(os.path.exists(os.path.join(settings.BLOCKS_PROCESSING_DATA, 'Code', 'Design', f"{block.true_LB_id.pk}", f"{block.true_LB_id.pk}.py"))):
                                        cycles.remove(block)
                                        spec = importlib.util.spec_from_file_location(f"{str(block.true_LB_id.pk)}.py", os.path.join(settings.BLOCKS_PROCESSING_DATA, 'Code', 'Design', f"{block.true_LB_id.pk}", f"{block.true_LB_id.pk}.py"))
                                        module = importlib.util.module_from_spec(spec)
                                        spec.loader.exec_module(module)
                                        blockOuts = module.execute(params_values_initials)
                                        true_blocks_out_intials["outputs"].append(blockOuts)
                                        if(os.path.exists(os.path.join(settings.BLOCK_OUTS, f"{str(block.network_id.pk)}", f"{str(block.true_LB_id.pk)}", f"{block.pk}.json"))):
                                            with open(os.path.join(settings.BLOCK_OUTS, f"{str(block.network_id.pk)}", f"{str(block.true_LB_id.pk)}", f"{block.pk}.json"), 'r') as rp:
                                                existing_outs = json.load(rp)
                                                existing_outs['outputs'].append(true_blocks_out_intials['outputs'][0])
                                            with open(os.path.join(settings.BLOCK_OUTS, f"{str(block.network_id.pk)}", f"{str(block.true_LB_id.pk)}", f"{block.pk}.json"), 'w') as wp:
                                                json.dump(existing_outs, wp, indent=4)
                                        else:
                                            os.makedirs(os.path.join(settings.BLOCK_OUTS, f"{str(block.network_id.pk)}", f"{str(block.true_LB_id.pk)}"), exist_ok=True)
                                            with open(os.path.join(settings.BLOCK_OUTS, f"{str(block.network_id.pk)}", f"{str(block.true_LB_id.pk)}", f"{block.pk}.json"), 'w') as wp:
                                                json.dump(true_blocks_out_intials, wp, indent=4)
                                    else:
                                        return JsonResponse({"status": "error", 'message': "code not found."})
                            else:
                                return JsonResponse({'status': 'error', 'message': f'circular dependency found ({[block.proxy_name for block in cycles]}).'})
                        else:
                            true_blocks_out = {
                                'blockId': block.pk,
                                'blockProxyName': block.proxy_name,
                                'outputs': []
                            }
                            params_values = get_inputs_block(block, iteration)
                            if(params_values):
                                print(params_values)
                                if(block.network_id.network_type == 'design'):
                                    if(os.path.exists(os.path.join(settings.BLOCKS_PROCESSING_DATA, 'Code', 'Design', f"{block.true_LB_id.pk}", f"{block.true_LB_id.pk}.py"))):
                                        spec = importlib.util.spec_from_file_location(f"{str(block.true_LB_id.pk)}.py", os.path.join(settings.BLOCKS_PROCESSING_DATA, 'Code', 'Design', f"{block.true_LB_id.pk}", f"{block.true_LB_id.pk}.py"))
                                        module = importlib.util.module_from_spec(spec)
                                        spec.loader.exec_module(module)
                                        blockOuts = module.execute(params_values)
                                        true_blocks_out["outputs"].append(blockOuts)
                                        if(os.path.exists(os.path.join(settings.BLOCK_OUTS, f"{str(block.network_id.pk)}", f"{str(block.true_LB_id.pk)}", f"{block.pk}.json"))):
                                            with open(os.path.join(settings.BLOCK_OUTS, f"{str(block.network_id.pk)}", f"{str(block.true_LB_id.pk)}", f"{block.pk}.json"), 'r') as rp:
                                                existing_outs = json.load(rp)
                                                existing_outs['outputs'].append(true_blocks_out['outputs'][0])
                                            with open(os.path.join(settings.BLOCK_OUTS, f"{str(block.network_id.pk)}", f"{str(block.true_LB_id.pk)}", f"{block.pk}.json"), 'w') as wp:
                                                json.dump(existing_outs, wp, indent=4)
                                        else:
                                            os.makedirs(os.path.join(settings.BLOCK_OUTS, f"{str(block.network_id.pk)}", f"{str(block.true_LB_id.pk)}"), exist_ok=True)
                                            with open(os.path.join(settings.BLOCK_OUTS, f"{str(block.network_id.pk)}", f"{str(block.true_LB_id.pk)}", f"{block.pk}.json"), 'w') as wp:
                                                json.dump(true_blocks_out, wp, indent=4)
                                    else:
                                        return JsonResponse({"status": "error", 'message': "code not found."})
                                elif(block.network_id.network_type == 'performance'):
                                    pass
                                elif(block.network_id.network_type == 'lifing'):
                                    pass
                                else:
                                    pass
                            else:
                                return JsonResponse({'status': 'error', 'message': 'check inputs outputs and code'})

                # Gather all outputs in JSON format
                all_blocks_outs = get_all_blocks_outputs(user_id)

                # ✅ Write to CSV after JSON
                import csv
                csv_output_dir = os.path.join(settings.BLOCK_OUTS, str(user_id))
                os.makedirs(csv_output_dir, exist_ok=True)

                csv_file_path = os.path.join(csv_output_dir, "simulation_output_{user_id}.csv")

                with open(csv_file_path, mode='w', newline='') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerow(["Block Proxy Name", "Iteration", "Output Key", "Output Value"])

                    for block in all_blocks_outs['all_blocks_outs']:
                        for i, iteration_out in enumerate(block['outputs']):
                            for key, value in iteration_out.items():
                                csv_writer.writerow([block['blockProxyName'], i, key, value])

                return JsonResponse({"status": "success", "message": "Blocks Executed Successfully.", "res": all_blocks_outs})
            else:
                raise NoBlockFoundError("No Blocks Detected to run...Please Drag and Drop the blocks")
        except NoBlockFoundError as nbf:
            print(nbf)
            return JsonResponse({"status": "error", "message": str(nbf)})
        except BlockDataError as bde:
            print(bde)
            return JsonResponse({"status": "error", "message": str(bde)})
        except Exception as e:
            print(f"from_view.py - {e}")
            return JsonResponse({"status": "error", "message": str(e)})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

# def run_simulation(request,user_id):
#     if(request.method == 'GET'):
#         try:
#             blocksExeOrder = get_execution_order(user_id)
#             all_blocks_outs = {'all_blocks_outs':[]}
#             if(len(blocksExeOrder)!=0):
#                 for block in blocksExeOrder:

#                     params_values = get_inputs_block(block)
#                     print(params_values)
#                     true_blocks_out = {'blockId':block.pk,
#                                        'blockProxyName':block.proxy_name,
#                                        'outputs':[]}
#                     if(params_values):
#                         if(block.network_id.network_type == 'design'):
#                             if(os.path.exists(os.path.join(settings.BLOCKS_PROCESSING_DATA,'Code','Design',f"{block.true_LB_id.pk}",f"{block.true_LB_id.pk}.py"))):
#                                 spec = importlib.util.spec_from_file_location(f"{str(block.true_LB_id.pk)}.py",os.path.join(settings.BLOCKS_PROCESSING_DATA,'Code','Design',f"{block.true_LB_id.pk}",f"{block.true_LB_id.pk}.py"))
#                                 module = importlib.util.module_from_spec(spec)
#                                 spec.loader.exec_module(module)
#                                 iteration = 2
#                                 for values in zip(*params_values.values()):
#                                     processing_values = dict(zip(params_values.keys(),values))
#                                     blockOuts = module.execute(processing_values)
#                                     true_blocks_out['outputs'].append(blockOuts)
#                                 if(os.path.exists(os.path.join(settings.BLOCK_OUTS,f"{str(block.network_id.pk)}",f"{str(block.true_LB_id.pk)}",f"{block.pk}.json"))):
#                                     with open(os.path.join(settings.BLOCK_OUTS,f"{str(block.network_id.pk)}",f"{str(block.true_LB_id.pk)}",f"{block.pk}.json"),'w') as wp:
#                                         json.dump(true_blocks_out,wp,indent=4)
#                                 else:
#                                     os.makedirs(os.path.join(settings.BLOCK_OUTS,f"{str(block.network_id.pk)}",f"{str(block.true_LB_id.pk)}"),exist_ok=True)
#                                     with open(os.path.join(settings.BLOCK_OUTS,f"{str(block.network_id.pk)}",f"{str(block.true_LB_id.pk)}",f"{block.pk}.json"),'w') as wp:
#                                         json.dump(true_blocks_out,wp,indent=4)
#                             else:
#                                 return JsonResponse({"status":"error",'message':"code not found."})
#                         elif(block.network_id.network_type == 'performance'):
#                             pass
#                         elif(block.network_id.network_type == 'lifing'):
#                             pass
#                         else:
#                             pass
#                         all_blocks_outs['all_blocks_outs'].append(true_blocks_out)
#                     else:
#                         return ({'status':'error','message':'check inputs outputs and code'})
#                 return JsonResponse({"status":"success","message":"Blocks Executed Successfully.","res":all_blocks_outs})
#             else:
#                 raise NoBlockFoundError("No Blocks Detected to run...Please Drag and Drop the blocks")
#         except NoBlockFoundError as nbf:
#             print(nbf)
#             return JsonResponse({"status": "error", "message": str(nbf)})
#         except BlockDataError as bde:
#             print(bde)
#             return JsonResponse({"status": "error", "message": str(bde)})
#         except Exception as e:
#             return JsonResponse({"status": "error", "message": str(e)})
#     else:
#         return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
# Block Connection related views    

def make_block_connection(request,user_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            functionSourceId = data['source_id']
            functionDestinationId = data['destination_id']

            functionBlockSourceInstance = functionBlockData.objects.get(pk=functionSourceId)
            functionBlockDestinationInstance = functionBlockData.objects.get(pk=functionDestinationId)
            networkInstance = Network.objects.get(pk=user_id)

            functionConnectionInstance = Connections(source=functionBlockSourceInstance,destination=functionBlockDestinationInstance,network_id = networkInstance)
            functionConnectionInstance.save()
            id = functionConnectionInstance.pk
            
            return JsonResponse({'status':'success','message':'connection inserted sucessfully','id':id})
        except Exception as e:
            print("error"+str(e))
            return JsonResponse({'status':'error','message':'connection not inserted sucessfully'})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def make_block_connection_reconst(request,user_id):
    if(request.method == 'POST'):
        try:
            
            id = json.loads(request.body)['id']
            src_id = json.loads(request.body)['source_id']
            dest_id = json.loads(request.body)['destination_id']

            srcInstance = functionBlockData.objects.get(pk=src_id)
            destInstance = functionBlockData.objects.get(pk=dest_id)
            
            networkInstance = Network.objects.get(pk=user_id)

            connectionInstance = Connections(id=id,destination=destInstance,source = srcInstance, network_id = networkInstance)
            connectionInstance.save()
            connection_instance_dict = {
                
                "id":connectionInstance.pk,
                "proxy_src":connectionInstance.source.proxy_name,
                "src":connectionInstance.source.pk,
                "proxy_dest":connectionInstance.destination.proxy_name,
                "dest":connectionInstance.destination.pk
            }

            return JsonResponse({'status':'success','message':'connection inserted sucessfully','connection_data':connection_instance_dict})
        except Exception as e:
            print(e)
            return JsonResponse({"status":"error","message":"failed to insert connection record"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def remove_function_block_connection(request,user_id):
    if(request.method == 'POST'):
        connectionId = json.loads(request.body)['connection_id']
        networkInstance = Network.objects.get(pk = user_id)
        connectionInstance = Connections.objects.get(pk = connectionId, network_id = networkInstance)

        destinationInstance = connectionInstance.destination
        destinationTrueId = destinationInstance.true_LB_id.pk
        destinationId = destinationInstance.pk

        sourceInstance = connectionInstance.source
        sourceId = sourceInstance.pk
        sourceProxyName = sourceInstance.proxy_name

        if(os.path.exists(os.path.join(settings.BLOCK_IO,f"{str(user_id)}",f"{str(destinationTrueId)}",f"{str(destinationId)}.json"))):

            with open(os.path.join(settings.BLOCK_IO,f"{str(user_id)}",f"{str(destinationTrueId)}",f"{str(destinationId)}.json"),'r') as rp:
                destinationInputsValues = json.load(rp)
            
            dependentOn = []
            proxyDependentOn = []
            for destinationInputsValue in destinationInputsValues['inputs_values']:
                if(destinationInputsValue['dependent']):
                    if(sourceId == destinationInputsValue['previous_block']):
                        dependentOn.append(sourceId)
                        proxyDependentOn.append(sourceProxyName)
                    else:
                        continue
                else:
                    continue
            
            if(len(dependentOn) == 0):
                connectionInstance.delete()
                return JsonResponse({"status":"success","remove":True,"redirect":False,"url":"","dependent_on":dependentOn,"dependent_proxy_name":proxyDependentOn})
            else:
                return JsonResponse({"status":"success","remove":False,"redirect":True,"url":f"{str(destinationTrueId)}/{str(destinationId)}/block_user_input_value","dependent_on":dependentOn,"dependent_proxy_name":proxyDependentOn})
            #     if(destinationInputsValue['dependent']):
            #         destinationInputsValue['dependent'] = False
            #         destinationInputsValue['previous_block'] = ""
            #         destinationInputsValue['previous_block_proxy'] = ""
            #         destinationInputsValue['previous_block_output'] = ""
            #         destinationInputsValue['previous_block_output_proxy'] = ""
            #     destinationInputsValuesInstance['inputs_values'].append(destinationInputsValue)
            # with open(os.path.join(settings.BLOCK_IO,f"{str(user_id)}",f"{str(destinationTrueId)}",f"{str(destinationId)}.json"),"w") as wp:
            #     json.dump(destinationInputsValuesInstance,wp,indent=4)

            # os.remove(os.path.join(settings.BLOCK_IO,f"{str(user_id)}",f"{str(destinationTrueId)}",f"{str(destinationId)}.json"))
            
            # return JsonResponse({"status":"success","message":"connection and dependent block IO deleted sucessfully"})
        else:
            connectionInstance.delete()
            return JsonResponse({"status":"success","message":"connection deleted sucessfully","remove":True})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def get_dest_block_num_connections(request,user_id):
    if(request.method == 'POST'):
        try:
            id = json.loads(request.body)['lineId']
            destinationInstance = Connections.objects.get(pk = id).destination
            connections = len(Connections.objects.filter(destination = destinationInstance))
            if(connections > 1):
                return JsonResponse({"status":"success","message":True,"connections":connections})
            else:
                return JsonResponse({"status":"success","message":False,"connections":connections})
        except Exception as e:
            print(e)
            return JsonResponse({"status":"error","message":str(e)})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def get_conncetion_existence(request,user_id):
    if(request.method == 'POST'):
        blockId = json.loads(request.body)['blockId']
        try:
            functionBlockInstance = functionBlockData.objects.get(network_id=user_id, id=blockId)
            asSourceInstance = Connections.objects.filter(network_id=user_id,source=functionBlockInstance).values()
            asDestinationInstance = Connections.objects.filter(network_id=user_id , destination=functionBlockInstance).values()

            asSourceList = [src for src in asSourceInstance]
            asDestList = [dest for dest in asDestinationInstance]

            asSourceDict = {"source":asSourceList}
            asDestDict = {"dest":asDestList}

            all = asSourceList + asDestList

            return JsonResponse({"status":'success',"as_source":asSourceDict,"as_dest":asDestDict,"all":all})
        except Exception as e:
            print(e)
            return JsonResponse({"status":"error","message":str(e)})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def get_function_block_dependencies(request,user_id,true_block_id,clone_block_id):
    if(request.method == 'GET'):
        cloneBlockId = clone_block_id
        dependencies = []
        try:

            functionBlockConnectionInstances = Connections.objects.filter(destination = cloneBlockId, network_id = user_id)
            for functionBlockConnectionInstance in functionBlockConnectionInstances:
                dependencies.append({"clone_id" : functionBlockConnectionInstance.source.pk,"proxy_name":functionBlockConnectionInstance.source.proxy_name})

            return JsonResponse({"status":"success","dependencies":dependencies})
        except Exception as e:
            print(e)
            return JsonResponse({"status":"error","message":"failed to fetch dependencies"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def export_network(network,filename):
    with open(filename+".json","w") as file:
        json.dump(network,file,indent=4)
    return {"status":"success","message":"network saved successfully","network":network}

def clear_all(request,user_id):
    if(request.method == "POST"):
        try:
            refresh = json.loads(request.body)['refresh']
            networkInstance = Network.objects.get(pk=user_id)
            Connections.objects.filter(network_id = networkInstance).delete()
            functionBlockData.objects.filter(network_id = networkInstance).delete()
            if(not refresh):
                if(os.path.exists(os.path.join(settings.BLOCK_IO,f"{str(user_id)}"))):
                    shutil.rmtree(os.path.join(settings.BLOCK_IO,f"{str(user_id)}"))

                if(os.path.exists(os.path.join(settings.BLOCK_OUTS,f"{str(user_id)}"))):
                    shutil.rmtree(os.path.join(settings.BLOCK_OUTS,f"{str(user_id)}"))
                    
                if(os.path.exists(os.path.join(settings.NETWORK_CURRENT_STATE,f"{str(user_id)}"))):
                    shutil.rmtree(os.path.join(settings.NETWORK_CURRENT_STATE,f"{str(user_id)}"))
                
                if(os.path.exists(os.path.join(settings.CIRCULAR_BLOCK_DEPENDENCY_DATA,f"{str(user_id)}"))):
                    shutil.rmtree(os.path.join(settings.CIRCULAR_BLOCK_DEPENDENCY_DATA,f"{str(user_id)}"))
                return JsonResponse({"status":"success"})
            
            else:
                return JsonResponse({"status":"success"})
        except Exception as e:
            print(e)
            return JsonResponse({'status':'error','message':str(e)})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def publish_block(request,block_id):
    if(request.method == 'GET'):
        logicBlockInstance = LogicBlocks.objects.get(pk = block_id)
        logicBlockInstance.publish = True
        logicBlockInstance.save()
        return JsonResponse({"status":"success","message":"blocks state changed"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

# blocks inputs populate views
def get_block_inputs_populate(request,user_id,true_block_id,clone_block_id):
    if(request.method == 'GET'):
        block_id = true_block_id
        try:
            if(os.path.exists(os.path.join(settings.BLOCK_IO,f"{str(user_id)}",f"{str(true_block_id)}",f"{str(clone_block_id)}.json"))):
                inputsValuesFile = os.path.join(settings.BLOCK_IO,f"{str(user_id)}",f"{str(true_block_id)}",f"{str(clone_block_id)}.json")
                with open(inputsValuesFile,'r') as rp:
                    inputsValuesInstance = json.load(rp)
                return JsonResponse({"status":"success","exists":True,"data":inputsValuesInstance})
            else:
                logicBlockInstance = LogicBlocks.objects.get(pk = block_id)
                logicBlockDesignInputs = logicBlockInstance.logic_block_design.all()
                design_inputs_all = []
                for logicBlockDesignInput in logicBlockDesignInputs:
                    design_inputs = {}
                    design_inputs['param_name'] = logicBlockDesignInput.param_name
                    design_inputs['unit'] = logicBlockDesignInput.unit
                    design_inputs_all.append(design_inputs)
                return JsonResponse({"status":"success","exists":False,"true_block_id":true_block_id,"clone_block_id":clone_block_id,"block_inputs":design_inputs_all})
        except Exception as e:
            print(e)
            return JsonResponse({"status":"error","messsage":"could not fetch the block inputs"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def get_block_initial_inputs_populate(request,user_id,true_block_id,clone_block_id):
    if(request.method == 'GET'):
        block_id = true_block_id
        try:
            if(os.path.exists(os.path.join(settings.CIRCULAR_BLOCK_DEPENDENCY_DATA,f"{str(user_id)}",f"{str(true_block_id)}",f"{str(clone_block_id)}.json"))):
                inputsValuesFile = os.path.join(settings.CIRCULAR_BLOCK_DEPENDENCY_DATA,f"{str(user_id)}",f"{str(true_block_id)}",f"{str(clone_block_id)}.json")
                with open(inputsValuesFile,'r') as rp:
                    inputsValuesInstance = json.load(rp)
                return JsonResponse({"status":"success","exists":True,"data":inputsValuesInstance})
            else:
                logicBlockInstance = LogicBlocks.objects.get(pk = block_id)
                logicBlockDesignInputs = logicBlockInstance.logic_block_design.all()
                design_inputs_all = []
                for logicBlockDesignInput in logicBlockDesignInputs:
                    design_inputs = {}
                    design_inputs['param_name'] = logicBlockDesignInput.param_name
                    design_inputs['unit'] = logicBlockDesignInput.unit
                    design_inputs_all.append(design_inputs)
                return JsonResponse({"status":"success","exists":False,"true_block_id":true_block_id,"clone_block_id":clone_block_id,"block_inputs":design_inputs_all})
        except Exception as e:
            print(e)
            return JsonResponse({"status":"error","messsage":"could not fetch the block inputs"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def go_back_to_home(request,user_id,true_block_id,clone_block_id):
    if(request.method == 'GET'):
        return JsonResponse({"status":"success","url":f"/{user_id}/simulate"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def get_user_inputs_value_url(request, user_id, true_block_id, clone_block_id):
    if request.method == 'GET':
        project_id = request.GET.get('project_id')
        category_type = request.GET.get('category_type')
        net_type = request.GET.get('net_type')

        # Print values to console for debugging
        print("project_id:", project_id)
        print("category_type:", category_type)
        print("net_type:", net_type)

        return JsonResponse({
            "status": "success",
            "url": f"{true_block_id}/{clone_block_id}/block_user_input_value"
        })

    return JsonResponse({
        "status": "error",
        "message": "Invalid request method"
    }, status=400)
    
def block_user_input_value(request,user_id,true_block_id,clone_block_id):
    if(request.method == "GET"): 
        project_id = request.GET.get('project_id')
        category_type = request.GET.get('category_type')
        net_type = request.GET.get('net_type')

        print(f"bu",project_id)
        print(f"bu",category_type)
        print(f"bu",net_type)

        context = {
            'project_id': project_id,
            'category_type': category_type,
            'net_type': net_type,
            'user_id': user_id,
        }
        return render(request,'user_block_input_value.html',context)
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
# logic block views

def save_logic_block_details(request):
    if(request.method == 'POST'):
        try:
            blocks_details_obj = LogicBlocks(
                module_id = Modules.objects.get(pk = request.POST.get('module_id')),
                submodule_id = SubModules.objects.get(pk = request.POST.get('submodule_id')),
                name = request.POST.get('logic_block_name'),
                block_type = request.POST.get('logic_block_type'),
                mode = request.POST.get('logic_block_mode')
            )
            blocks_details_obj.save()
            return redirect("showAdminPanel")
        except Exception as e:
            print(e)
            return JsonResponse({"status":"error","message":"failed to save block details"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def retrieve_logic_blocks(request):
    if(request.method == 'GET'):
        try:
            trueLBs = []
            LBs = LogicBlocks.objects.all()
            for LB in LBs:  
                trueLBs.append({"block_name":LB.name,"block_id":LB.pk})
            return JsonResponse({'status':'success','logicblocks':trueLBs})
        except Exception as e:
            return JsonResponse({"status": "error", "message":"error occured while fetching block datas"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def remove_logic_block(request):
    if(request.method == 'POST'):
        blockId = request.POST.get('logic_block_id')
        try:
            LogicBlocks.objects.get(pk=blockId).delete()

            return redirect('showAdminPanel')
        except Exception as e:
            print(e)
            return JsonResponse({"status":"error","message":"please select a block."})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def LB_inputs(request,block_id):
    if(request.method == 'GET'):
        return render(request,'logic_block_user_input.html')
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def get_block_user_inputs_ui(request,block_id):
    if(request.method == 'GET'):
        return JsonResponse({"status":"success","user_input_url":f"{block_id}/LB_inputs"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def put_design_params(request,block_id):
    if(request.method == 'POST'):
        if(block_id):
            try:
                actual_block_id = LogicBlocks.objects.get(pk = block_id)
                design_params = json.loads(request.body)['design_params']
                for design_param in design_params:
                    pu = list(design_param.values())
                    if(pu[0] and pu[1]):
                        LogicBlocksDesignParams(LB_id = actual_block_id, param_name = pu[0], unit = pu[1]).save()

                return JsonResponse({"status":"success","message":"Design Params saved successfully"})
            except Exception as e:
                print(e)
                return JsonResponse({"status":"error","message":"Design parmas not saved."})
        else:
            return JsonResponse({"status":"error","message":"block_id is null, should contain a block id"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def put_preformance_params(request,block_id):
    if(request.method == 'POST'):
        if(block_id):
            try:
                actual_block_id = LogicBlocks.objects.get(pk = block_id)
                performance_params = json.loads(request.body)['performance_params']
                for performance_param in performance_params:
                    pu = list(performance_param.values())
                    if(pu[0] and pu[1]):
                        LogicBlocksPerformanceParams(LB_id = actual_block_id, param_name = pu[0], unit = pu[1]).save()
                return JsonResponse({"status":"success","message":"Performance Params saved successfully"})
            except Exception as e:
                print(e)
                return JsonResponse({"status":"error","message":"Performance parmas not saved."})
        else:
            return JsonResponse({"status":"error","message":"block_id is null, should contain a block id"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def put_lifing_params(request,block_id):
    if(request.method == 'POST'):
        if(block_id):
            try:
                actual_block_id = LogicBlocks.objects.get(pk = block_id)
                lifing_params = json.loads(request.body)['lifing_params']
                for lifing_param in lifing_params:
                    pu = list(lifing_param.values())
                    if(pu[0] and pu[1]):
                        LogicBlocksLifingParams(LB_id = actual_block_id, param_name = pu[0], unit = pu[1]).save()

                return JsonResponse({"status":"success","message":"Lifing Params saved successfully"})
            except Exception as e:
                print(e)
                return JsonResponse({"status":"error","message":"Lifing parmas not saved."})
        else:
            return JsonResponse({"status":"error","message":"block_id is null, should contain a block id"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def put_prognostic_params(request,block_id):
    if(request.method == 'POST'):
        if(block_id):
            try:
                actual_block_id = LogicBlocks.objects.get(pk = block_id)
                prognostic_params = json.loads(request.body)['prognostic_params']
                for prognostic_param in prognostic_params:
                    pu = list(prognostic_param.values())
                    if(pu[0] and pu[1]):
                        LogicBlocksPrognosticParams(LB_id = actual_block_id, param_name = pu[0], unit = pu[1]).save()

                return JsonResponse({"status":"success","message":"Prognostic Params saved successfully"})
            except Exception as e:
                print(e)
                return JsonResponse({"status":"error","message":"Prognostic parmas not saved."})
        else:
            return JsonResponse({"status":"error","message":"block_id is null, should contain a block id"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def delete_design_input(request,block_id):
    if(request.method == 'POST'):
        record_id = json.loads(request.body)['record_id']
        try:
            LogicBlocksDesignParams.objects.get(pk = record_id,LB_id = block_id).delete()
            return JsonResponse({"status":"success","message":"design input deleted succesfully"})
        except Exception as e:
            print(e)
            return JsonResponse({"status":"error","message":"design parameter not deleted"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def delete_performance_input(request,block_id):
    if(request.method == 'POST'):
        record_id = json.loads(request.body)['record_id']
        try:
            LogicBlocksPerformanceParams.objects.get(pk = record_id,LB_id = block_id).delete()
            return JsonResponse({"status":"success","message":"Performance input deleted succesfully"})
        except Exception as e:
            print(e)
            return JsonResponse({"status":"error","message":"Performance parameter not deleted"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def delete_lifing_input(request,block_id):
    if(request.method == 'POST'):
        record_id = json.loads(request.body)['record_id']
        try:
            LogicBlocksLifingParams.objects.get(pk = record_id,LB_id = block_id).delete()
            return JsonResponse({"status":"success","message":"Lifing input deleted succesfully"})
        except Exception as e:
            print(e)
            return JsonResponse({"status":"error","message":"Lifing parameter not deleted"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def delete_prognostics_input(request,block_id):
    if(request.method == 'POST'):
        record_id = json.loads(request.body)['record_id']
        try:
            LogicBlocksPrognosticParams.objects.get(pk = record_id,LB_id = block_id).delete()
            return JsonResponse({"status":"success","message":"Prognostic input deleted succesfully"})
        except Exception as e:
            print(e)
            return JsonResponse({"status":"error","message":"Prognostic parameter not deleted"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def get_edit_block_user_ui(request,block_id):
    if(request.method == 'GET'):
        return JsonResponse({"status":'success','edit_input_params':f"{block_id}/edit_LB_inputs"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def edit_LB_inputs(request,block_id):
    if(request.method == 'GET'):
        return render(request,'logic_block_inputs_edit.html')
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def get_design_params(request,block_id):
    if(request.method == 'GET'):
        true_design_params = []
        try:
            design_params = LogicBlocksDesignParams.objects.filter(LB_id = block_id)
            for design_param in design_params:
                true_design_params.append({'param_name':design_param.param_name,'unit':design_param.unit,'id':design_param.pk})
            return JsonResponse({'status':'success',"input_params":true_design_params})
        except Exception as e:
            return JsonResponse({'status':'error','message':'input params not found'})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def get_performance_params(request,block_id):
    if(request.method == 'GET'):
        true_performance_params = []
        try:
            performance_params = LogicBlocksPerformanceParams.objects.filter(LB_id = block_id)
            for performance_param in performance_params:
                true_performance_params.append({'param_name':performance_param.param_name,'unit':performance_param.unit,'id':performance_param.pk})
            return JsonResponse({'status':'success',"input_params":true_performance_params})
        except Exception as e:
            return JsonResponse({'status':'error','message':'input params not found'})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def get_lifing_params(request,block_id):
    if(request.method == 'GET'):
        true_lifing_params = []
        try:
            lifing_params = LogicBlocksLifingParams.objects.filter(LB_id = block_id)
            for lifing_param in lifing_params:
                true_lifing_params.append({'param_name':lifing_param.param_name,'unit':lifing_param.unit,'id':lifing_param.pk})
            return JsonResponse({'status':'success',"input_params":true_lifing_params})
        except Exception as e:
            return JsonResponse({'status':'error','message':'input params not found'})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def get_prognostic_params(request,block_id):
    if(request.method == 'GET'):
        true_prognostic_params = []
        try:
            prognostic_params = LogicBlocksPrognosticParams.objects.filter(LB_id = block_id)
            for prognostic_param in prognostic_params:
                true_prognostic_params.append({'param_name':prognostic_param.param_name,'unit':prognostic_param.unit,'id':prognostic_param.pk})
            return JsonResponse({'status':'success',"input_params":true_prognostic_params})
        except Exception as e:
            return JsonResponse({'status':'error','message':'input params not found'})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def put_edited_design_params(request,block_id):
    if(request.method == 'POST'):
        print("hi from design")
        edited_params = json.loads(request.body)['design_edited_params']
        print(type(edited_params),len(edited_params))
        try:
            for edited_param in edited_params:
                print(edited_param)
                if(edited_param['id']!='NONE'):
                    design_input_record = LogicBlocksDesignParams.objects.get(LB_id = block_id,pk = edited_param['id'])
                    design_input_record.param_name = edited_param['param_name']
                    design_input_record.unit = edited_param['unit']
                   
                    design_input_record.save()
                else:
                    block_obj = LogicBlocks.objects.get(pk=block_id)
                    LogicBlocksDesignParams(LB_id = block_obj, param_name = edited_param['param_name'], unit = edited_param['unit']).save()
            return JsonResponse({'status':'success','message':'parameters edited successfully'})
        except Exception as e:
            print(e)
            return JsonResponse({"status":"error","message":"failed to update input params"})        
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def put_edited_performance_params(request,block_id):
    if(request.method == 'POST'):
        edited_params = json.loads(request.body)['performance_edited_params']
        print(edited_params)
        for edited_param in edited_params:
            try:
                if(edited_param['id']!='NONE'):
                    performance_input_record = LogicBlocksPerformanceParams.objects.get(LB_id = block_id,pk = edited_param['id'])
                    performance_input_record.param_name = edited_param['param_name']
                    performance_input_record.unit = edited_param['unit']

                    performance_input_record.save()
                else:
                    block_obj = LogicBlocks.objects.get(pk=block_id)
                    LogicBlocksPerformanceParams(LB_id = block_obj, param_name = edited_param['param_name'], unit = edited_param['unit']).save()
            except Exception as e:
                print(e)
                return JsonResponse({"status":"error","message":"failed to update input params"})
        return JsonResponse({'status':'success','message':'parameters edited successfully'})            
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def put_edited_lifing_params(request,block_id):
    if(request.method == 'POST'):
        edited_params = json.loads(request.body)['lifing_edited_params']
        for edited_param in edited_params:
            try:
                if(edited_param['id']!='NONE'):
                    lifing_input_record = LogicBlocksLifingParams.objects.get(LB_id = block_id,pk = edited_param['id'])
                    lifing_input_record.param_name = edited_param['param_name']
                    lifing_input_record.unit = edited_param['unit']

                    lifing_input_record.save()
                else:
                    block_obj = LogicBlocks.objects.get(pk=block_id)
                    LogicBlocksLifingParams(LB_id = block_obj, param_name = edited_param['param_name'], unit = edited_param['unit']).save()
                
            except Exception as e:
                print(e)
                return JsonResponse({"status":"error","message":"failed to update input params"})
        return JsonResponse({'status':'success','message':'parameters edited successfully'})        
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def put_edited_prognostic_params(request,block_id):
    if(request.method == 'POST'):
        edited_params = json.loads(request.body)['prognostic_edited_params']
        for edited_param in edited_params:
            try:
                if(edited_param['id']!='NONE'):
                    prognostic_input_record = LogicBlocksPrognosticParams.objects.get(LB_id = block_id,pk = edited_param['id'])
                    prognostic_input_record.param_name = edited_param['param_name']
                    prognostic_input_record.unit = edited_param['unit']

                    prognostic_input_record.save()
                else:
                    block_obj = LogicBlocks.objects.get(pk=block_id)
                    LogicBlocksPrognosticParams(LB_id = block_obj, param_name = edited_param['param_name'], unit = edited_param['unit']).save()
            except Exception as e:
                print(e)
                return JsonResponse({"status":"error","message":"failed to update input params"})
        return JsonResponse({'status':'success','message':'parameters edited successfully'})    
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
    # code editor and processing views
def get_code_editor_ui(request,block_id):
    if(request.method == 'GET'):
        return JsonResponse({'status':'success',"code_editor_url":f"{block_id}/LB-code-editor"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def LB_code_editor(request,block_id):
    if(request.method == "GET"):
        return render(request,'codeEditor.html')
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def put_LB_Design_Code(request,block_id):
    if(request.method == 'POST'):
        LBCode = json.loads(request.body)['LBCode']
        BLOCKS_PROCESSING_DATA_folder = settings.BLOCKS_PROCESSING_DATA
        BLOCKS_PROCESSING_DATA_code_folder = os.path.join(BLOCKS_PROCESSING_DATA_folder,'Code')
        BLOCKS_PROCESSING_DATA_code_design_folder = os.path.join(BLOCKS_PROCESSING_DATA_code_folder,'Design')
        BLOCKS_PROCESSING_DATA_code_design_specific_folder = os.path.join(BLOCKS_PROCESSING_DATA_code_design_folder,str(f"{block_id}"))

        os.makedirs(BLOCKS_PROCESSING_DATA_code_design_specific_folder,exist_ok=True)

        if(os.path.exists(BLOCKS_PROCESSING_DATA_code_design_specific_folder)):
            BLOCKS_PROCESSING_DATA_code_design_specific_py_file = os.path.join(BLOCKS_PROCESSING_DATA_code_design_specific_folder,f'{block_id}.py')
            try:
                with open(BLOCKS_PROCESSING_DATA_code_design_specific_py_file ,'w') as wp:
                    wp.write(LBCode)
                return JsonResponse({"status":"success","message":"code save in file"})
            except Exception as e:
                print(e)
                return JsonResponse({"status":"error","message":"code not saved in file"})
        else:
            return JsonResponse({"status":"error","message":"folder not found."})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def put_LB_Performance_Code(request,block_id):
    if(request.method == 'POST'):
        LBCode = json.loads(request.body)['LBCode']
        BLOCKS_PROCESSING_DATA_folder = settings.BLOCKS_PROCESSING_DATA
        BLOCKS_PROCESSING_DATA_code_folder = os.path.join(BLOCKS_PROCESSING_DATA_folder,'Code')
        BLOCKS_PROCESSING_DATA_code_performance_folder = os.path.join(BLOCKS_PROCESSING_DATA_code_folder,'Performance')
        BLOCKS_PROCESSING_DATA_code_performance_specific_folder = os.path.join(BLOCKS_PROCESSING_DATA_code_performance_folder,str(f"{block_id}"))

        os.makedirs(BLOCKS_PROCESSING_DATA_code_performance_specific_folder,exist_ok=True)

        if(os.path.exists(BLOCKS_PROCESSING_DATA_code_performance_specific_folder)):
            BLOCKS_PROCESSING_DATA_code_performance_specific_py_file = os.path.join(BLOCKS_PROCESSING_DATA_code_performance_specific_folder,f'{block_id}.py')
            try:
                with open(BLOCKS_PROCESSING_DATA_code_performance_specific_py_file ,'w') as wp:
                    wp.write(LBCode)
                return JsonResponse({"status":"success","message":"code save in file"})
            except Exception as e:
                print(e)
                return JsonResponse({"status":"error","message":"code not saved in file"})
        else:
            return JsonResponse({"status":"error","message":"folder not found."})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def put_LB_Lifing_Code(request,block_id):
    if(request.method == 'POST'):
        LBCode = json.loads(request.body)['LBCode']
        BLOCKS_PROCESSING_DATA_folder = settings.BLOCKS_PROCESSING_DATA
        BLOCKS_PROCESSING_DATA_code_folder = os.path.join(BLOCKS_PROCESSING_DATA_folder,'Code')
        BLOCKS_PROCESSING_DATA_code_lifing_folder = os.path.join(BLOCKS_PROCESSING_DATA_code_folder,'Lifing')
        BLOCKS_PROCESSING_DATA_code_lifing_specific_folder = os.path.join(BLOCKS_PROCESSING_DATA_code_lifing_folder,str(f"{block_id}"))

        os.makedirs(BLOCKS_PROCESSING_DATA_code_lifing_specific_folder,exist_ok=True)

        if(os.path.exists(BLOCKS_PROCESSING_DATA_code_lifing_specific_folder)):
            BLOCKS_PROCESSING_DATA_code_lifing_specific_py_file = os.path.join(BLOCKS_PROCESSING_DATA_code_lifing_specific_folder,f'{block_id}.py')
            try:
                with open(BLOCKS_PROCESSING_DATA_code_lifing_specific_py_file ,'w') as wp:
                    wp.write(LBCode)
                return JsonResponse({"status":"success","message":"code save in file"})
            except Exception as e:
                print(e)
                return JsonResponse({"status":"error","message":"code not saved in file"})
        else:
            return JsonResponse({"status":"error","message":"folder not found."})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def put_LB_Prognostic_Code(request,block_id):
    if(request.method == 'POST'):
        LBCode = json.loads(request.body)['LBCode']
        BLOCKS_PROCESSING_DATA_folder = settings.BLOCKS_PROCESSING_DATA
        BLOCKS_PROCESSING_DATA_code_folder = os.path.join(BLOCKS_PROCESSING_DATA_folder,'Code')
        BLOCKS_PROCESSING_DATA_code_prognostic_folder = os.path.join(BLOCKS_PROCESSING_DATA_code_folder,'Prognostic')
        BLOCKS_PROCESSING_DATA_code_prognostic_specific_folder = os.path.join(BLOCKS_PROCESSING_DATA_code_prognostic_folder,str(f"{block_id}"))

        os.makedirs(BLOCKS_PROCESSING_DATA_code_prognostic_specific_folder,exist_ok=True)

        if(os.path.exists(BLOCKS_PROCESSING_DATA_code_prognostic_specific_folder)):
            BLOCKS_PROCESSING_DATA_code_prognostic_specific_py_file = os.path.join(BLOCKS_PROCESSING_DATA_code_prognostic_specific_folder,f'{block_id}.py')
            try:
                with open(BLOCKS_PROCESSING_DATA_code_prognostic_specific_py_file ,'w') as wp:
                    wp.write(LBCode)
                return JsonResponse({"status":"success","message":"code save in file"})
            except Exception as e:
                print(e)
                return JsonResponse({"status":"error","message":"code not saved in file"})
        else:
            return JsonResponse({"status":"error","message":"folder not found."})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def get_edit_block_code_editor_ui(request,block_id):
    if(request.method == 'GET'):
        return JsonResponse({'status':'success','edit_code_editor_ui_url':f"{block_id}/LB-edit-code-CodeEditor"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def LB_edit_code_editor(request,block_id):
    if(request.method == 'GET'):
        return render(request,'edit_code_editor.html')
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def get_design_code(request,block_id):
    if(request.method == 'GET'):
        pyFilesFolder = f'fluidsim/Blocks_Processing_Data/Code/Design/{block_id}'
        try:
            pyFiles = os.listdir(pyFilesFolder)

            if(pyFiles[0]):
                pyFile = os.path.join(pyFilesFolder,pyFiles[0])
                with open(pyFile, 'r') as rp:
                    code = rp.read()
                return JsonResponse({"status":"success","code":code})
            else:
                return JsonResponse({"status":"success","code":"no code"})
        except Exception as e:
            return JsonResponse({"status":"success","code":"no code"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def get_performance_code(request,block_id):
    if(request.method == 'GET'):
        pyFilesFolder = f'fluidsim/Blocks_Processing_Data/Code/Performance/{block_id}'
        try:
            pyFiles = os.listdir(pyFilesFolder)

            if(pyFiles[0]):
                pyFile = os.path.join(pyFilesFolder,pyFiles[0])
                with open(pyFile, 'r') as rp:
                    code = rp.read()
                return JsonResponse({"status":"success","code":code})
            else:
                return JsonResponse({"status":"success","code":"no code"})
        except Exception as e:
            return JsonResponse({"status":"success","code":"no code"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def get_lifing_code(request,block_id):
    if(request.method == 'GET'):
        pyFilesFolder = f'fluidsim/Blocks_Processing_Data/Code/Lifing/{block_id}'
        try:
            pyFiles = os.listdir(pyFilesFolder)

            if(pyFiles[0]):
                pyFile = os.path.join(pyFilesFolder,pyFiles[0])
                with open(pyFile, 'r') as rp:
                    code = rp.read()
                return JsonResponse({"status":"success","code":code})
            else:
                return JsonResponse({"status":"success","code":"no code"})
        except Exception as e:
            return JsonResponse({"status":"success","code":"no code"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def get_prognostic_code(request,block_id):
    if(request.method == 'GET'):
        pyFilesFolder = f'fluidsim/Blocks_Processing_Data/Code/Prognostics/{block_id}'
        try:
            pyFiles = os.listdir(pyFilesFolder)

            if(pyFiles[0]):
                pyFile = os.path.join(pyFilesFolder,pyFiles[0])
                with open(pyFile, 'r') as rp:
                    code = rp.read()
                return JsonResponse({"status":"success","code":code})
            else:
                return JsonResponse({"status":"success","code":"no code"})
        except Exception as e:
            return JsonResponse({"status":"success","code":"no code"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    

def put_design_edited_code(request,block_id):
    if(request.method == 'POST'):
        code = json.loads(request.body)['code']
        codeTypeFolder = f'fluidsim/Blocks_Processing_Data/Code/Design'
        if(not(os.path.exists(os.path.join(codeTypeFolder,f"{str(block_id)}")))):    
            os.makedirs(os.path.join(codeTypeFolder,f"{str(block_id)}",exist_ok=True))

        pyFilesFolder = f'fluidsim/Blocks_Processing_Data/Code/Design/{block_id}'

        try:
            pyfile = os.path.join(pyFilesFolder,f"{str(block_id)}.py")
            with open(pyfile,'w') as wp:
                wp.write(code)
            return JsonResponse({"status":"success","admin_url":"/admin_panel/"})
        except Exception as e:
            return JsonResponse({"status":"error","message":"Code not updated"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def put_performance_edited_code(request,block_id):
    if(request.method == 'POST'):
        code = json.loads(request.body)['code']
        codeTypeFolder = f'fluidsim/Blocks_Processing_Data/Code/Performance'
        if(not(os.path.exists(os.path.join(codeTypeFolder,f"{str(block_id)}")))):    
            os.makedirs(os.path.join(codeTypeFolder,f"{str(block_id)}"),exist_ok=True)

        pyFilesFolder = f'fluidsim/Blocks_Processing_Data/Code/Performance/{block_id}'

        try:
            pyfile = os.path.join(pyFilesFolder,f"{str(block_id)}.py")
            with open(pyfile,'w') as wp:
                wp.write(code)
            return JsonResponse({"status":"success","admin_url":"/admin_panel/"})
        except Exception as e:
            return JsonResponse({"status":"error","message":"Code not updated"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def put_lifing_edited_code(request,block_id):
    if(request.method == 'POST'):
        code = json.loads(request.body)['code']
        codeTypeFolder = f'fluidsim/Blocks_Processing_Data/Code/Lifing'
        if(not(os.path.exists(os.path.join(codeTypeFolder,f"{str(block_id)}")))):    
            os.makedirs(os.path.join(codeTypeFolder,f"{str(block_id)}"),exist_ok=True)

        pyFilesFolder = f'fluidsim/Blocks_Processing_Data/Code/Lifing/{block_id}'

        try:
            pyfile = os.path.join(pyFilesFolder,f"{str(block_id)}.py")
            with open(pyfile,'w') as wp:
                wp.write(code)
            return JsonResponse({"status":"success","admin_url":"/admin_panel/"})
        except Exception as e:
            return JsonResponse({"status":"error","message":"Code not updated"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def put_prognostic_edited_code(request,block_id):
    if(request.method == 'POST'):
        code = json.loads(request.body)['code']
        codeTypeFolder = f'fluidsim/Blocks_Processing_Data/Code/Prognostic'
        if(not(os.path.exists(os.path.join(codeTypeFolder,f"{str(block_id)}")))):    
            os.makedirs(os.path.join(codeTypeFolder,f"{str(block_id)}"),exist_ok=True)

        pyFilesFolder = f'fluidsim/Blocks_Processing_Data/Code/Prognostic/{block_id}'

        try:
            pyfile = os.path.join(pyFilesFolder,f"{str(block_id)}.py")
            with open(pyfile,'w') as wp:
                wp.write(code)
            return JsonResponse({"status":"success","admin_url":"/admin_panel/"})
        except Exception as e:
            return JsonResponse({"status":"error","message":"Code not updated"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def get_block_user_outputs_ui(request,block_id):
    if(request.method == 'GET'):
        return JsonResponse({"status":"success","user_output_url":f"{block_id}/LB_outputs"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def LB_outputs(request,block_id):
    if(request.method == 'GET'):
        return render(request,'logic_block_outputs.html')
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def put_design_out_params(request,block_id):
    if(request.method == 'POST'):
        if(block_id):
            try:
                actual_block_id = LogicBlocks.objects.get(pk = block_id)
                design_params = json.loads(request.body)['design_params']
                for design_param in design_params:
                    pu = list(design_param.values())
                    if(pu[0] and pu[1]):
                        LogicBlockDesignOutputs(LB_id = actual_block_id, out_param_name = pu[0], unit = pu[1]).save()

                return JsonResponse({"status":"success","message":"Design Params saved successfully"})
            except Exception as e:
                print(e)
                return JsonResponse({"status":"error","message":"Design parmas not saved."})
        else:
            return JsonResponse({"status":"error","message":"block_id is null, should contain a block id"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def put_preformance_out_params(request,block_id):
    if(request.method == 'POST'):
        if(block_id):
            try:
                actual_block_id = LogicBlocks.objects.get(pk = block_id)
                performance_params = json.loads(request.body)['performance_params']
                for performance_param in performance_params:
                    pu = list(performance_param.values())
                    if(pu[0] and pu[1]):
                        LogicBlockPerformanceOutputs(LB_id = actual_block_id, out_param_name = pu[0], unit = pu[1]).save()
                return JsonResponse({"status":"success","message":"Performance Params saved successfully"})
            except Exception as e:
                print(e)
                return JsonResponse({"status":"error","message":"Performance parmas not saved."})
        else:
            return JsonResponse({"status":"error","message":"block_id is null, should contain a block id"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def put_lifing_out_params(request,block_id):
    if(request.method == 'POST'):
        if(block_id):
            try:
                actual_block_id = LogicBlocks.objects.get(pk = block_id)
                lifing_params = json.loads(request.body)['lifing_params']
                for lifing_param in lifing_params:
                    pu = list(lifing_param.values())
                    if(pu[0] and pu[1]):
                        LogicBlockLifingOutputs(LB_id = actual_block_id, out_param_name = pu[0], unit = pu[1]).save()

                return JsonResponse({"status":"success","message":"Lifing Params saved successfully"})
            except Exception as e:
                print(e)
                return JsonResponse({"status":"error","message":"Lifing parmas not saved."})
        else:
            return JsonResponse({"status":"error","message":"block_id is null, should contain a block id"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def put_prognostic_out_params(request,block_id):
    if(request.method == 'POST'):
        if(block_id):
            try:
                actual_block_id = LogicBlocks.objects.get(pk = block_id)
                prognostic_params = json.loads(request.body)['prognostic_params']
                for prognostic_param in prognostic_params:
                    pu = list(prognostic_param.values())
                    if(pu[0] and pu[1]):
                        LogicBlockPrognosticOutputs(LB_id = actual_block_id, out_param_name = pu[0], unit = pu[1]).save()

                return JsonResponse({"status":"success","message":"Prognostic Params saved successfully"})
            except Exception as e:
                print(e)
                return JsonResponse({"status":"error","message":"Prognostic parmas not saved."})
        else:
            return JsonResponse({"status":"error","message":"block_id is null, should contain a block id"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    

def get_edit_block_output_user_ui(request,block_id):
    if(request.method == 'GET'):
        return JsonResponse({"status":'success','edit_output_params':f"{block_id}/edit_LB_outputs"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def edit_LB_outputs(request,block_id):
    if(request.method == 'GET'):
        return render(request,'logic_block_outputs_edit.html')
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def get_design_output_params(request,block_id):
    if(request.method == 'GET'):
        true_design_params = []
        try:
            design_params = LogicBlockDesignOutputs.objects.filter(LB_id = block_id)
            for design_param in design_params:
                true_design_params.append({'param_name':design_param.out_param_name,'unit':design_param.unit,'id':design_param.pk})
            print(true_design_params)
            return JsonResponse({'status':'success',"input_params":true_design_params})
        except Exception as e:
            print(e)
            return JsonResponse({'status':'error','message':'input params not found'})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def get_performance_output_params(request,block_id):
    if(request.method == 'GET'):
        true_performance_params = []
        try:
            performance_params = LogicBlockPerformanceOutputs.objects.filter(LB_id = block_id)
            for performance_param in performance_params:
                true_performance_params.append({'param_name':performance_param.out_param_name,'unit':performance_param.unit,'id':performance_param.pk})
            return JsonResponse({'status':'success',"input_params":true_performance_params})
        except Exception as e:
            return JsonResponse({'status':'error','message':'input params not found'})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def get_lifing_output_params(request,block_id):
    if(request.method == 'GET'):
        true_lifing_params = []
        try:
            lifing_params = LogicBlockLifingOutputs.objects.filter(LB_id = block_id)
            for lifing_param in lifing_params:
                true_lifing_params.append({'param_name':lifing_param.out_param_name,'unit':lifing_param.unit,'id':lifing_param.pk})
            return JsonResponse({'status':'success',"input_params":true_lifing_params})
        except Exception as e:
            return JsonResponse({'status':'error','message':'input params not found'})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def get_prognostic_output_params(request,block_id):
    if(request.method == 'GET'):
        true_prognostic_params = []
        try:
            prognostic_params = LogicBlockPrognosticOutputs.objects.filter(LB_id = block_id)
            for prognostic_param in prognostic_params:
                true_prognostic_params.append({'param_name':prognostic_param.out_param_name,'unit':prognostic_param.unit,'id':prognostic_param.pk})
            return JsonResponse({'status':'success',"input_params":true_prognostic_params})
        except Exception as e:
            return JsonResponse({'status':'error','message':'input params not found'})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def delete_design_output(request,block_id):
    if(request.method == 'POST'):
        record_id = json.loads(request.body)['record_id']
        try:
            LogicBlockDesignOutputs.objects.get(pk = record_id,LB_id = block_id).delete()
            return JsonResponse({"status":"success","message":"design output deleted succesfully"})
        except Exception as e:
            print(e)
            return JsonResponse({"status":"error","message":"design parameter not deleted"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def delete_performance_output(request,block_id):
    if(request.method == 'POST'):
        record_id = json.loads(request.body)['record_id']
        try:
            LogicBlockPerformanceOutputs.objects.get(pk = record_id,LB_id = block_id).delete()
            return JsonResponse({"status":"success","message":"Performance input deleted succesfully"})
        except Exception as e:
            print(e)
            return JsonResponse({"status":"error","message":"Performance parameter not deleted"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def delete_lifing_output(request,block_id):
    if(request.method == 'POST'):
        record_id = json.loads(request.body)['record_id']
        try:
            LogicBlockLifingOutputs.objects.get(pk = record_id,LB_id = block_id).delete()
            return JsonResponse({"status":"success","message":"Lifing input deleted succesfully"})
        except Exception as e:
            print(e)
            return JsonResponse({"status":"error","message":"Lifing parameter not deleted"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def delete_prognostics_output(request,block_id):
    if(request.method == 'POST'):
        record_id = json.loads(request.body)['record_id']
        try:
            LogicBlockPrognosticOutputs.objects.get(pk = record_id,LB_id = block_id).delete()
            return JsonResponse({"status":"success","message":"Prognostic input deleted succesfully"})
        except Exception as e:
            print(e)
            return JsonResponse({"status":"error","message":"Prognostic parameter not deleted"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def put_edited_design_output(request,block_id):
    if(request.method == 'POST'):
        print("hi from design")
        edited_params = json.loads(request.body)['design_edited_params']
        print(type(edited_params),len(edited_params))
        try:
            for edited_param in edited_params:
                print(edited_param)
                if(edited_param['id']!='NONE'):
                    design_input_record = LogicBlockDesignOutputs.objects.get(LB_id = block_id,pk = edited_param['id'])
                    design_input_record.out_param_name = edited_param['param_name']
                    design_input_record.unit = edited_param['unit']
                   
                    design_input_record.save()
                else:
                    block_obj = LogicBlocks.objects.get(pk=block_id)
                    LogicBlockDesignOutputs(LB_id = block_obj, out_param_name = edited_param['param_name'], unit = edited_param['unit']).save()
            return JsonResponse({'status':'success','message':'parameters edited successfully'})
        except Exception as e:
            print(e)
            return JsonResponse({"status":"error","message":"failed to update input params"})        
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def put_edited_performance_output(request,block_id):
    if(request.method == 'POST'):
        edited_params = json.loads(request.body)['performance_edited_params']
        print(edited_params)
        for edited_param in edited_params:
            try:
                if(edited_param['id']!='NONE'):
                    performance_input_record = LogicBlockPerformanceOutputs.objects.get(LB_id = block_id,pk = edited_param['id'])
                    performance_input_record.param_name = edited_param['param_name']
                    performance_input_record.unit = edited_param['unit']

                    performance_input_record.save()
                else:
                    block_obj = LogicBlocks.objects.get(pk=block_id)
                    LogicBlockPerformanceOutputs(LB_id = block_obj, out_param_name = edited_param['param_name'], unit = edited_param['unit']).save()
            except Exception as e:
                print(e)
                return JsonResponse({"status":"error","message":"failed to update input params"})
        return JsonResponse({'status':'success','message':'parameters edited successfully'})            
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def put_edited_lifing_output(request,block_id):
    if(request.method == 'POST'):
        edited_params = json.loads(request.body)['lifing_edited_params']
        for edited_param in edited_params:
            try:
                if(edited_param['id']!='NONE'):
                    lifing_input_record = LogicBlockLifingOutputs.objects.get(LB_id = block_id,pk = edited_param['id'])
                    lifing_input_record.param_name = edited_param['param_name']
                    lifing_input_record.unit = edited_param['unit']

                    lifing_input_record.save()
                else:
                    block_obj = LogicBlocks.objects.get(pk=block_id)
                    LogicBlockLifingOutputs(LB_id = block_obj, out_param_name = edited_param['param_name'], unit = edited_param['unit']).save()
                
            except Exception as e:
                print(e)
                return JsonResponse({"status":"error","message":"failed to update input params"})
        return JsonResponse({'status':'success','message':'parameters edited successfully'})        
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def put_edited_prognostic_output(request,block_id):
    if(request.method == 'POST'):
        edited_params = json.loads(request.body)['prognostic_edited_params']
        for edited_param in edited_params:
            try:
                if(edited_param['id']!='NONE'):
                    prognostic_input_record = LogicBlockPrognosticOutputs.objects.get(LB_id = block_id,pk = edited_param['id'])
                    prognostic_input_record.param_name = edited_param['param_name']
                    prognostic_input_record.unit = edited_param['unit']

                    prognostic_input_record.save()
                else:
                    block_obj = LogicBlocks.objects.get(pk=block_id)
                    LogicBlockPrognosticOutputs(LB_id = block_obj, out_param_name = edited_param['param_name'], unit = edited_param['unit']).save()
            except Exception as e:
                print(e)
                return JsonResponse({"status":"error","message":"failed to update input params"})
        return JsonResponse({'status':'success','message':'parameters edited successfully'})    
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    

# developer login
from django.contrib.auth import authenticate, login
from django.contrib import messages

def developer_login_view(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')

        user=authenticate(request,username=username,password=password)
        if user is not None:
            # Check if user is in the 'Simulation user' group
            if user.groups.filter(name='Developer').exists():
                login(request, user)
                return redirect('developer_dashboard')  # Success login
            else:
                messages.error(request, "Access denied: You are not authorized to log in here.")
        else:
            messages.error(request, "Invalid username or password.")
        
        # Return to landing page in both failure cases
        return render(request, 'landingpage.html')
    return render(request, 'developer_dashboard.html')

def User_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Check if user is in the 'Simulation user' group
            if user.groups.filter(name='Simulation User').exists():
                login(request, user)
                return redirect('project_selection')  # Success login
            else:
                messages.error(request, "Access denied: You are not authorized to log in here.")
        else:
            messages.error(request, "Invalid username or password.")
        
        # Return to landing page in both failure cases
        return render(request, 'landingpage.html')

    # For GET request show login page (e.g., index)
    return render(request, 'selection_page.html')


def Admin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Check if user is in the 'Simulation user' group
            if user.groups.filter(name='Simulation Admin').exists():
                login(request, user)
                return redirect('/admin_panel/')  # Success login
            else:
                messages.error(request, "Access denied: You are not authorized to log in here.")
        else:
            messages.error(request, "Invalid username or password.")
        
        # Return to landing page in both failure cases
        return render(request, 'landingpage.html')

    # For GET request show login page (e.g., index)
    return render(request, 'admin_panel.html')




def developer_dashboard(request):
    groups = Group.objects.all()
    users = User.objects.all().prefetch_related('groups')

    # Prepare module and submodule structure
    modules_data = []
    all_modules = Modules.objects.prefetch_related('submodules').all()
    for module in all_modules:
        modules_data.append({
            'id': module.id,
            'name': module.name,
            'submodules': list(module.submodules.values('id', 'name')),
        })

    # Map: user_id -> set of module_ids
    user_module_map = {
        user.id: set(UserModuleAccess.objects.filter(user=user).values_list('module__id', flat=True))
        for user in users
    }

    # Map: user_id -> set of submodule_ids
    user_submodule_map = {
        user.id: set(UserSubmoduleAccess.objects.filter(user=user).values_list('submodule__id', flat=True))
        for user in users
    }

    return render(request, 'developer_dashboard.html', {
        'groups': groups,
        'users': users,
        'modules_data': modules_data,
        'user_module_map': user_module_map,
        'user_submodule_map': user_submodule_map,
    })



from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_protect

def create_groups(request):
    if request.method=="POST":
        group_name=request.POST.get('group_name')
        if group_name:
            Group.objects.get_or_create(name=group_name)

            return redirect('developer_dashboard')
        else:
            messages.error(request,"Group not Created")

    return render(request,'developer_dashboard.html')
    
def create_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        group_id = request.POST.get('group')

        if username and password and group_id:
            # Create the user
            user = User.objects.create_user(username=username, password=password)

            # Add user to selected group
            group = Group.objects.get(id=group_id)
            user.groups.add(group)

            messages.success(request, f'User "{username}" created and added to group "{group.name}".')
            return redirect('developer_dashboard')  # Use the name of your user management view

    # fallback
    return render(request,'developer_dashboard.html')


# module access visibility

from django.shortcuts import get_object_or_404, redirect


def set_user_visibility(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)

        # Clear previous settings
        UserModuleAccess.objects.filter(user=user).delete()
        UserSubmoduleAccess.objects.filter(user=user).delete()

        selected_modules = request.POST.getlist("modules")
        selected_submodules = request.POST.getlist("submodules")

        # Track modules that are saved (either directly or from submodules)
        saved_module_ids = set()

        # Save selected modules first
        for module_id in selected_modules:
            module = get_object_or_404(Modules, id=module_id)
            UserModuleAccess.objects.create(user=user, module=module)
            saved_module_ids.add(module.id)

        # Save selected submodules
        for submodule_id in selected_submodules:
            submodule = get_object_or_404(SubModules, id=submodule_id)
            UserSubmoduleAccess.objects.create(user=user, submodule=submodule)

            # Ensure the parent module of submodule is also saved
            parent_module = submodule.module
            if parent_module.id not in saved_module_ids:
                UserModuleAccess.objects.create(user=user, module=parent_module)
                saved_module_ids.add(parent_module.id)

        return redirect('developer_dashboard')
    
    
## fetching the user based projects ####
def get_user_networks_forsharing(request, user_id):
    projects = simulationproject.objects.filter(user_id=user_id)
    project_list = [{"project_id": p.id, "project_name": p.project_name} for p in projects]
    return JsonResponse({"projects": project_list})

        
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@require_POST
def share_project(request):
    data = json.loads(request.body)
    project_id = data.get("project_id")
    to_user_id = data.get("to_user_id")

    print(f"hi",project_id)
    print(f"hi",to_user_id)

    try:
        source_project = simulationproject.objects.get(id=project_id)
        target_user = User.objects.get(id=to_user_id)

        # Step 1: Duplicate the project for the target user
        new_project = simulationproject.objects.create(
            user=target_user,
            project_name=source_project.project_name,
            category_type=source_project.category_type,
            net_type=source_project.net_type
        )

        # Step 2: Copy user network files
        # Old path: USER_NETWORKS/source_user_id/project_id
        source_path = os.path.join(
            settings.USER_NETWORKS,
            str(source_project.user.id),
            str(source_project.id)
        )
        dest_path = os.path.join(
            settings.USER_NETWORKS,
            str(to_user_id),
            str(new_project.id)
        )

        if os.path.exists(source_path):
            shutil.copytree(source_path, dest_path)

        return JsonResponse({"message": "Project shared successfully."})

    except simulationproject.DoesNotExist:
        return JsonResponse({"error": "Source project does not exist."}, status=404)
    except User.DoesNotExist:
        return JsonResponse({"error": "Target user does not exist."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# def share_network(request):
#     data = json.loads(request.body)
#     source_id = data["source_user_id"]
#     target_id = data["target_user_id"]
#     network_name = data["network_name"]

#     # USER_NETWORKS logic (unchanged)
#     source_path = os.path.join(settings.USER_NETWORKS, str(source_id), network_name)
#     target_path = os.path.join(settings.USER_NETWORKS, str(target_id), network_name)

#     if not os.path.exists(source_path):
#         return JsonResponse({"message": "Source network not found."}, status=404)

#     if os.path.exists(target_path):
#         return JsonResponse({"message": "Network already exists for this user."}, status=409)

#     shutil.copytree(source_path, target_path)

#     # NETWORK_INPUT_FILES logic (copy all .csv and .xlsx from source to target)
#     source_input_folder = os.path.join(settings.NETWORK_INPUT_FILES, str(source_id))
#     target_input_folder = os.path.join(settings.NETWORK_INPUT_FILES, str(target_id))

#     os.makedirs(target_input_folder, exist_ok=True)

#     for file_name in os.listdir(source_input_folder):
#         if file_name.endswith('.csv') or file_name.endswith('.xlsx'):
#             source_file = os.path.join(source_input_folder, file_name)
#             target_file = os.path.join(target_input_folder, file_name)

#             # Only copy if target doesn't already have it
#             if not os.path.exists(target_file):
#                 shutil.copy2(source_file, target_file)

#     return JsonResponse({"message": "Network and input files shared successfully."})





def change_user_group(request,user_id):
    if request .method=='POST':
        user=get_object_or_404(User, id=user_id)
        new_group_id=request.POST.get('group')

        if new_group_id:
            new_group=get_object_or_404(Group, id=new_group_id)

            user.groups.clear()
            user.groups.add(new_group)
            messages.success(request, f"{user.username}'s group updated to {new_group}.")
    return redirect('developer_dashboard')


def project_selection(request):
    user_projects = simulationproject.objects.filter(user=request.user)

    project_networks = {}
    categories = ["Controllers", "Design", "Lifing", "Performance", "Prognostics"]
    net_types = ["1D", "2D", "3D"]

    user_dir = os.path.join(settings.USER_NETWORKS, str(request.user.id))

    for project in user_projects:
        project_id = str(project.id)
        project_networks[project_id] = {}

        for category in categories:
            project_networks[project_id][category] = {}

            for net_type in net_types:
                net_path = os.path.join(user_dir, project_id, category, net_type)
                network_data = []

                if os.path.exists(net_path):
                    for folder_name in os.listdir(net_path):
                        folder_path = os.path.join(net_path, folder_name)
                        network_file = os.path.join(folder_path, 'network.json')

                        if os.path.isfile(network_file):
                            try:
                                with open(network_file, "r") as f:
                                    content = json.load(f)
                                    network_data.append({
                                        "filename": folder_name,  
                                        "content": content
                                    })
                            except Exception as e:
                                network_data.append({
                                    "filename": folder_name,
                                    "content": f"Error loading file: {str(e)}"
                                })

                project_networks[project_id][category][net_type] = network_data

    return render(
        request,
        'selection_page.html',
        {
            'user_projects': user_projects,
            'project_networks': project_networks,
            'categories': categories,
            'net_types': net_types
        }
    )

def simulate_project(request, user_id):
    if request.method == 'POST':
        project_name = request.POST.get('project_name')
        category_type = request.POST.get('category_type')
        net_type = request.POST.get('net_type')

        print(project_name)
        print(category_type)
        print(net_type)

        if project_name and category_type and net_type:
            if net_type == '1D':
                project = simulationproject.objects.create(
                    user=request.user,
                    project_name=project_name,
                    category_type=category_type,
                    net_type=net_type
                )
                return redirect(
                    f'/{request.user.id}/simulate?project_id={project.id}&category_type={project.category_type}&net_type={project.net_type}'
                )
            else:
                return redirect('project_selection')
    return redirect('project_selection')


def simulate_existing_project(request, user_id):
    if request.method == "POST":
        project_id = request.POST.get('projectSelect')
        category_type = request.POST.get('category_type1')
        net_type = request.POST.get('net_type1')

        print(f"fsf",project_id)
        print(category_type)
        print(net_type)

        if project_id and category_type and net_type:
            if net_type == '1D':
                return redirect(
                    f'/{request.user.id}/simulate?project_id={project_id}&category_type={category_type}&net_type={net_type}'
                )
            else:
                return JsonResponse({'status': 'error', 'message': 'Wrong network type selected'})
        else:
           return JsonResponse({'status': 'error', 'message': 'Wrong '})
        
    return redirect('project_selection')

def get_user_project_structure(request, user_id):
    user_dir = os.path.join(settings.USER_NETWORKS, str(user_id))
    structure = []

    projects = simulationproject.objects.filter(user_id=user_id)

    for project in projects:
        project_entry = {
            "project_id": project.id,
            "project_name": project.project_name,
            "categories": []
        }

        project_path = os.path.join(user_dir, str(project.id))
        if os.path.exists(project_path):
            for category in os.listdir(project_path):
                category_path = os.path.join(project_path, category)
                if not os.path.isdir(category_path):
                    continue

                category_entry = {
                    "category_name": category,
                    "net_types": []
                }

                for net_type in os.listdir(category_path):
                    net_type_path = os.path.join(category_path, net_type)
                    if not os.path.isdir(net_type_path):
                        continue

                    files = [
                        f for f in os.listdir(net_type_path)
                        if os.path.isdir(os.path.join(net_type_path, f))
                    ]

                    category_entry["net_types"].append({
                        "net_type": net_type,
                        "files": files
                    })

                project_entry["categories"].append(category_entry)

        structure.append(project_entry)

    return JsonResponse({"structure": structure})


def get_all_users(request):
    users = User.objects.values("id", "username")
    return JsonResponse({"users": list(users)})

def get_user_projects(request, user_id):
    projects = simulationproject.objects.filter(user_id=user_id).values("id", "project_name").distinct()
    print(f"sdhf",projects)
    return JsonResponse({"projects": list(projects)})

# def push_network(request):
#     data = json.loads(request.body)

#     src_user = str(data['source_user_id'])
#     src_prj_id=str(data['source_prj_id'])
#     tgt_user = str(data['target_user_id'])
#     file_name = data['file_name']
#     project_id = str(data['project_id'])
#     category_type = data['category_type']
#     net_type = data['net_type']

#     print(f"sp",src_prj_id)
#     print(f"dp",project_id)

#     src_path = os.path.join(
#         settings.USER_NETWORKS, src_user, src_prj_id, category_type, net_type, file_name
#     )
#     dst_path = os.path.join(
#         settings.USER_NETWORKS, tgt_user,project_id, category_type, net_type, file_name
#     )
#     print(src_path)
#     print(dst_path)
#     try:
#         os.makedirs(dst_path, exist_ok=True)

#         shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
#         return JsonResponse({"message": "File pushed successfully."})
#     except Exception as e:
#         return JsonResponse({"message": f"Error pushing file: {str(e)}"}, status=500)

def push_network(request):
    data = json.loads(request.body)

    src_user = str(data['source_user_id'])
    src_prj_id = str(data['source_prj_id'])
    tgt_user = str(data['target_user_id'])
    file_name = data['file_name']
    project_id = str(data['project_id'])
    category_type = data['category_type']
    net_type = data['net_type']
    action = data.get("action")  # override or create_new or None

    src_path = os.path.join(settings.USER_NETWORKS, src_user, src_prj_id, category_type, net_type, file_name)
    base_dst_dir = os.path.join(settings.USER_NETWORKS, tgt_user, project_id, category_type, net_type)
    dst_path = os.path.join(base_dst_dir, file_name)

    if not os.path.exists(src_path):
        return JsonResponse({"message": "Source path does not exist."}, status=400)

    if os.path.exists(dst_path):
        if action == "override":
            shutil.rmtree(dst_path)
        elif action == "create_new":
            copy_index = 1
            new_file_name = f"{file_name}_copy"
            while os.path.exists(os.path.join(base_dst_dir, new_file_name)):
                new_file_name = f"{file_name}_copy{copy_index}"
                copy_index += 1
            dst_path = os.path.join(base_dst_dir, new_file_name)
        else:
            # File exists but no action specified: ask frontend
            return JsonResponse({
                "message": "File with this name already exists.",
                "status": "exists"
            }, status=200)

    try:
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copytree(src_path, dst_path)
        return JsonResponse({
            "message": "File pushed successfully.",
            "new_file_name": os.path.basename(dst_path),
            "status": "success"
        })
    except Exception as e:
        return JsonResponse({"message": f"Error pushing file: {str(e)}"}, status=500)
    

from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

@csrf_protect
@require_POST
def delete_project(request, user_id, project_id):
    try:
        project_path = os.path.join(settings.USER_NETWORKS, str(user_id), str(project_id))
        if os.path.exists(project_path):
            shutil.rmtree(project_path)

            simulationproject.objects.filter(id=project_id, user_id=user_id).delete()

            return JsonResponse({"message": "Project deleted successfully."})
        else:
            return JsonResponse({"message": "Project not found."}, status=404)
    except Exception as e:
        return JsonResponse({"message": f"Error deleting project: {str(e)}"}, status=500)

def delete_network_file(request, user_id, project_id, category_type, net_type, file_name):
    try:
        base_path = os.path.join(settings.USER_NETWORKS, str(user_id), str(project_id), category_type, net_type, file_name)
        if os.path.exists(base_path):
            shutil.rmtree(base_path)
            return JsonResponse({"message": "Network deleted successfully."})
        else:
            return JsonResponse({"message": "Network folder not found."}, status=404)
    except Exception as e:
        return JsonResponse({"message": f"Error deleting network: {str(e)}"}, status=500)