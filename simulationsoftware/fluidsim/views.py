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

def home(request,net_id):
    return render(request,'home.html')

def save_network_details(request):
    if(request.method == 'POST'):
        networkName = request.POST.get("network_name")
        networkType = request.POST.get("network_type")
        try:
            networkInstance = Network(name = networkName, network_type = networkType)
            networkInstance.save()
            networkId = networkInstance.pk

            return redirect(f"/{networkId}/simulate")
         
        except Exception as e:
            return redirect("index")
    else:
        return JsonResponse({'status':'error','message':'Invalid request'})
    
def save_network_current_state(request,net_id):
    if(request.method == 'POST'):
        networkState = json.loads(request.body)['state']
        try:
            if(os.path.exists(os.path.join(settings.NETWORK_CURRENT_STATE,f"{str(net_id)}"))):
                with open(os.path.join(settings.NETWORK_CURRENT_STATE,f"{str(net_id)}","current_network_state.json"),'w') as wp:
                    json.dump(networkState,wp,indent=4)
                return JsonResponse({"status":"success","message":"saved Current State."}) 
            else:
                os.makedirs(os.path.join(settings.NETWORK_CURRENT_STATE,f"{str(net_id)}"),exist_ok=True)
                with open(os.path.join(settings.NETWORK_CURRENT_STATE,f"{str(net_id)}","current_network_state.json"),'w') as wp:
                    json.dump(networkState,wp,indent=4)
                return JsonResponse({"status":"success","message":"saved Current State."}) 
            
        except Exception as e:
            print(e)
            return JsonResponse({"status":"error","message":f"{str(e)}"}) 
    else:
        return JsonResponse({'status':'error','message':'Invalid request'})

def get_network_current_state(request,net_id):
    if(request.method == 'GET'):
        print("*******enter******")
        try:
            networkCurrentState = None
            if(os.path.join(settings.NETWORK_CURRENT_STATE,f"{str(net_id)}","current_network_state.json")):
                with open(os.path.join(settings.NETWORK_CURRENT_STATE,f"{str(net_id)}","current_network_state.json"),'r') as rp:
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
    
def save_network_excel_csv(request,net_id):
    if(request.method == 'POST'):
        files = request.FILES.getlist('files')
        networkInputFolder = os.path.join(settings.NETWORK_INPUT_FILES,f"{str(net_id)}")
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
                os.makedirs(os.path.join(settings.NETWORK_INPUT_FILES,f"{str(net_id)}"),exist_ok=True)
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
    
def get_network_excel_uploads(request,net_id,true_block_id,clone_block_id):
    if(request.method == 'GET'):
        try:
            network_input_folder = os.path.join(settings.NETWORK_INPUT_FILES,f"{str(net_id)}")
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

def get_user_selected_excel_columns(request,net_id,true_block_id,clone_block_id):
    if(request.method == 'POST'):
        value = json.loads(request.body)['excel_name']
        try:
            network_input_file = os.path.join(settings.NETWORK_INPUT_FILES,f"{str(net_id)}",f"{value}")
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
    
def get_blocks_outputs(request,net_id,true_block_id,clone_block_id):
    if(request.method=='POST'):
        try:
            previousBlockId = json.loads(request.body)['previous_block_id']; 
        
            networkInstace = Network.objects.get(pk=net_id)
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
    
def put_block_input_values(request,net_id,true_block_id,clone_block_id):
    if(request.method == 'POST'):
        blocksIOroot = settings.BLOCK_IO
        inputs_values = json.loads(request.body)
        try:
            if(not os.path.exists(os.path.join(blocksIOroot,f"{str(net_id)}"))):
                os.makedirs(os.path.join(blocksIOroot,f"{str(net_id)}",f"{str(true_block_id)}"),exist_ok=True)
                IOJsonFile = os.path.join(blocksIOroot,f"{str(net_id)}",f"{str(true_block_id)}",f"{str(clone_block_id)}.json")
                with open(IOJsonFile,'w') as wp:
                    json.dump(inputs_values,wp,indent=4)
            else:
                if(not os.path.exists(os.path.join(blocksIOroot,f"{str(net_id)}",f"{str(true_block_id)}"))):
                    os.makedirs(os.path.join(blocksIOroot,f"{str(net_id)}",f"{str(true_block_id)}"),exist_ok=True)
                    IOJsonFile = os.path.join(blocksIOroot,f"{str(net_id)}",f"{str(true_block_id)}",f"{str(clone_block_id)}.json")
                    with open(IOJsonFile,'w') as wp:
                        json.dump(inputs_values,wp,indent=4)
                else:
                    IOJsonFile = os.path.join(blocksIOroot,f"{str(net_id)}",f"{str(true_block_id)}",f"{str(clone_block_id)}.json")
                    with open(IOJsonFile,'w') as wp:
                        json.dump(inputs_values,wp,indent=4)
            return JsonResponse({"status":"success","message":"input values saved."})
        except Exception as e:
            print(e)

    else:
        return JsonResponse({'status':'error','message':'Invalid Request'})
    
def put_block_initial_input_values(request,net_id,true_block_id,clone_block_id):
    if(request.method == 'POST'):
        blocksIOroot = settings.CIRCULAR_BLOCK_DEPENDENCY_DATA
        inputs_values = json.loads(request.body)
        try:
            if(not os.path.exists(os.path.join(blocksIOroot,f"{str(net_id)}"))):
                os.makedirs(os.path.join(blocksIOroot,f"{str(net_id)}",f"{str(true_block_id)}"),exist_ok=True)
                IOJsonFile = os.path.join(blocksIOroot,f"{str(net_id)}",f"{str(true_block_id)}",f"{str(clone_block_id)}.json")
                with open(IOJsonFile,'w') as wp:
                    json.dump(inputs_values,wp,indent=4)
            else:
                if(not os.path.exists(os.path.join(blocksIOroot,f"{str(net_id)}",f"{str(true_block_id)}"))):
                    os.makedirs(os.path.join(blocksIOroot,f"{str(net_id)}",f"{str(true_block_id)}"),exist_ok=True)
                    IOJsonFile = os.path.join(blocksIOroot,f"{str(net_id)}",f"{str(true_block_id)}",f"{str(clone_block_id)}.json")
                    with open(IOJsonFile,'w') as wp:
                        json.dump(inputs_values,wp,indent=4)
                else:
                    IOJsonFile = os.path.join(blocksIOroot,f"{str(net_id)}",f"{str(true_block_id)}",f"{str(clone_block_id)}.json")
                    with open(IOJsonFile,'w') as wp:
                        json.dump(inputs_values,wp,indent=4)
            return JsonResponse({"status":"success","message":"input values saved."})
        except Exception as e:
            print(e)

    else:
        return JsonResponse({'status':'error','message':'Invalid Request'})
    


from django.contrib.auth.decorators import login_required

@login_required
def get_tree_data(request, net_id):
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
def put_function_block_clone(request,net_id):
    if(request.method == 'POST'):
        try:
            data = json.loads(request.body)

            id = data['id']
            true_id = data["true_id"]

            trueLBInstance = LogicBlocks.objects.get(pk=true_id)
            networkInstance = Network.objects.get(pk=net_id)

            functionBlockInstance = functionBlockData(id=id,true_LB_id=trueLBInstance,network_id = networkInstance)
            functionBlockInstance.save()

            return JsonResponse({'status': 'success','message': 'Record inserted successfully'})
        except Exception as e:
            print(e)
            return JsonResponse({'stauts': 'error','message':'record not inserted'}, status=404)
    else:
        return JsonResponse({'status':'error','message':'Invalid request method'},status=400)
    
def put_function_block_clone_recon(request,net_id):
    if(request.method == 'POST'):
        id = json.loads(request.body)['id']
        true_LB_id = json.loads(request.body)['true_LB_id']
        proxy_name = json.loads(request.body)['proxy_name']
        try:
            networkInstance = Network.objects.get(pk=net_id)
            trueBlockInstance = LogicBlocks.objects.get(pk=true_LB_id)

            functionBlockData(pk=id,true_LB_id=trueBlockInstance,network_id=networkInstance,proxy_name=proxy_name).save()

            return JsonResponse({'status': 'success','message': 'Record inserted successfully'})

        except Exception as e:
            print(e)
            return JsonResponse({'status':"error","message":"failed to insert Record"})
    else:
        return JsonResponse({'status':'error','message':'Invalid request method'},status=400)

def put_function_block_name(request,net_id):
    if(request.method == 'POST'):
        try:
            block_name = json.loads(request.body)['user_block_name']
            id = json.loads(request.body)['clone_id']

            functionInsatnce = functionBlockData.objects.get(id=id,network_id=net_id)
            functionInsatnce.proxy_name = block_name
            functionInsatnce.save()

            return JsonResponse({'status': 'success','message': 'Block Name added'})
        except Exception as e:
            print(e)
            return JsonResponse({'stauts': 'error','message':'record not inserted'}, status=404)
    else:
        return JsonResponse({'status':'error','message':'Invalid request method'},status=400)
    
def delete_function_block_clone(request,net_id):
    if(request.method == 'POST'):
        try:
            data = json.loads(request.body)
            id = data['id']

            networkInstance = Network.objects.get(pk=net_id)
            functionBlockInstance = functionBlockData.objects.get(id = id,network_id = networkInstance)
            true_id = functionBlockInstance.true_LB_id.pk
            deleted_connections = list(Connections.objects.filter(source=functionBlockInstance) | Connections.objects.filter(destination=functionBlockInstance))
            deleted_connections_id = [id.pk for id in deleted_connections]
            
            functionBlockInstance.delete()
            if(os.path.exists(os.path.join(settings.BLOCK_IO,f"{str(net_id)}",f"{str(true_id)}",f"{str(id)}.json"))):
                os.remove(os.path.join(settings.BLOCK_IO,f"{str(net_id)}",f"{str(true_id)}",f"{str(id)}.json"))
                if(os.path.exists(os.path.join(settings.CIRCULAR_BLOCK_DEPENDENCY_DATA,f"{str(net_id)}",f"{str(true_id)}",f"{str(id)}.json"))):
                    os.remove(os.path.join(settings.CIRCULAR_BLOCK_DEPENDENCY_DATA,f"{str(net_id)}",f"{str(true_id)}",f"{str(id)}.json"))
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
    
def save_user_network(request,net_id):
    if(request.method == 'POST'):
        workspacePostionState = json.loads(request.body)['workspacePostionState']
        fileName = json.loads(request.body)['myfilename']

        # save network
        if(not os.path.exists(os.path.join(settings.USER_NETWORKS,f"{str(net_id)}"))):
            os.makedirs(os.path.join(settings.USER_NETWORKS,f"{str(net_id)}"),exist_ok=True)
            
            if(not os.path.exists(os.path.join(settings.USER_NETWORKS,f"{str(net_id)}",f"{str(fileName)}"))):
                os.makedirs(os.path.join(settings.USER_NETWORKS,f"{str(net_id)}",f"{str(fileName)}"),exist_ok=True)
                
                userSaveFile = os.path.join(settings.USER_NETWORKS,f"{str(net_id)}",f"{str(fileName)}","network.json")
                with open(userSaveFile,"w") as wp:
                    json.dump(workspacePostionState,wp,indent=4)

                saved_network_inputs_values = save_user_network_inputs_values(request,net_id,fileName)
                if(saved_network_inputs_values):
                    return JsonResponse({"status":'success',"message":'network and its related block IO saved successfully'})
                else:
                    return JsonResponse({"status":'success',"message":'network and saved successfully'})
            else:
                userSaveFile = os.path.join(settings.USER_NETWORKS,f"{str(net_id)}",f"{str(fileName)}","network.json")
                with open(userSaveFile,"w") as wp:
                    json.dump(workspacePostionState,wp,indent=4)

                saved_network_inputs_values = save_user_network_inputs_values(request,net_id,fileName)
                if(saved_network_inputs_values):
                    return JsonResponse({"status":'success',"message":'network and its related block IO saved successfully'})
                else:
                    return JsonResponse({"status":'success',"message":'network and saved successfully'})
               
            
        else:
            if(not os.path.exists(os.path.join(settings.USER_NETWORKS,f"{str(net_id)}",f"{str(fileName)}"))):
                os.makedirs(os.path.join(settings.USER_NETWORKS,f"{str(net_id)}",f"{str(fileName)}"),exist_ok=True)

                userSaveFile = os.path.join(settings.USER_NETWORKS,f"{str(net_id)}",f"{str(fileName)}","network.json")
                with open(userSaveFile,"w") as wp:
                    json.dump(workspacePostionState,wp,indent=4)

                saved_network_inputs_values = save_user_network_inputs_values(request,net_id,fileName)
                if(saved_network_inputs_values):
                    return JsonResponse({"status":'success',"message":'network and its related block IO saved successfully'})
                else:
                    return JsonResponse({"status":'success',"message":'network and saved successfully'})

            else:
                userSaveFile = os.path.join(settings.USER_NETWORKS,f"{str(net_id)}",f"{str(fileName)}","network.json")
                with open(userSaveFile,"w") as wp:
                    json.dump(workspacePostionState,wp,indent=4)

                saved_network_inputs_values = save_user_network_inputs_values(request,net_id,fileName)
                if(saved_network_inputs_values):
                    return JsonResponse({"status":'success',"message":'network and its related block IO saved successfully'})
                else:
                    return JsonResponse({"status":'success',"message":'network and saved successfully'})
            
        # save network block inputs
    else:
        return JsonResponse({'status':'error','message':'Invalid request method'},status=400)

def save_user_network_inputs_values(request,net_id,fileName):
    try:
        if(os.path.exists(os.path.join(settings.USER_NETWORKS,f"{str(net_id)}",f"{str(fileName)}"))):
            if(os.path.exists(os.path.join(settings.USER_NETWORKS,f"{str(net_id)}",f"{str(fileName)}","inputs_values"))):
                shutil.rmtree(os.path.join(settings.USER_NETWORKS,f"{str(net_id)}",f"{str(fileName)}","inputs_values"))
                if(os.path.exists(os.path.join(settings.BLOCK_IO,f"{str(net_id)}"))):
                    shutil.copytree(os.path.join(settings.BLOCK_IO,f"{str(net_id)}"),os.path.join(settings.USER_NETWORKS,f"{str(net_id)}",f"{str(fileName)}","inputs_values"))
                    return True
                else:
                    return False
            else:
                if(os.path.exists(os.path.join(settings.BLOCK_IO,f"{str(net_id)}"))):
                    # os.makedirs(os.path.join(settings.USER_NETWORKS,f"{str(net_id)}",f"{str(fileName)}","inputs_values"),exist_ok=True)
                    shutil.copytree(os.path.join(settings.BLOCK_IO,f"{str(net_id)}"),os.path.join(settings.USER_NETWORKS,f"{str(net_id)}",f"{str(fileName)}","inputs_values"))
                    return True
                else:
                    return False
        return False
    except Exception as e:
        print(e)
    
def get_user_networks(request,net_id):
    if(request.method == "GET"):
        if(os.path.exists(os.path.join(settings.USER_NETWORKS,f"{str(net_id)}"))):
            trueNetworkFolderNames = os.listdir(os.path.join(settings.USER_NETWORKS,f"{str(net_id)}"))
            if(len(trueNetworkFolderNames)!=0):
                networkFolderNames = []
                for trueNetworkFolderName in trueNetworkFolderNames: 
                    name = trueNetworkFolderName.split(".json")[0]
                    networkFolderNames.append(name)
                return JsonResponse({"status":"success","network_files":networkFolderNames})
            else:
                return JsonResponse({"status":"success",'message':"no networks found"})
        else:
            return JsonResponse({"status:success",'error',"folder not found to fetch networks"})
    else:
        return JsonResponse({'status':'error','message':'Invalid request method'},status=400)
    
def get_user_selected_network(request,net_id):
    if(request.method == "POST"):
        network_name = json.loads(request.body)['network_name']
        if(os.path.exists(os.path.join(settings.USER_NETWORKS,f"{str(net_id)}",f"{network_name}","network.json"))):
            network_file = os.path.join(settings.USER_NETWORKS,f"{str(net_id)}",f"{network_name}",f"network.json")

            with open(network_file,"r") as rp:
                networkInstance = json.load(rp)
            # load_inputs_values = load_user_inputs_to_folder(request,net_id,network_name)
            # if(load_inputs_values):
            #     return JsonResponse({"status":"success","message":"BLOCK IO loaded and also network","network":networkInstance,})
            # else:
            return JsonResponse({"status":"success","message":"network loaded","network":networkInstance,})
        else:
            return JsonResponse({"status":"error","message":"file not found"})
    else:
        return JsonResponse({'status':'error','message':'Invalid request method'},status=400)
    
def load_user_inputs_to_folder(request,net_id):
    if(request.method == 'POST'):
        network_name = json.loads(request.body)['network_name']
        if(os.path.exists(os.path.join(settings.USER_NETWORKS,f"{str(net_id)}",f"{network_name}",f"inputs_values"))):
            shutil.copytree(src=os.path.join(settings.USER_NETWORKS,f"{str(net_id)}",f"{str(network_name)}","inputs_values"),dst=os.path.join(settings.BLOCK_IO,f"{str(net_id)}"))
            # for root,dirs,files in os.walk(os.path.join(settings.USER_NETWORKS,f"{str(net_id)}",f"{network_name}",f"inputs_values")):
            #     print(os.path.realpath(root,(os.path.join(settings.BLOCK_IO,f"{str(net_id)}"))))
            return JsonResponse({'status':'success','message':'added'})
        else:
            return JsonResponse({"status":"success","message":"no related inputs values"})
    else:
        return JsonResponse({'status':'error','message':'Invalid request method'},status=400)

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

def run_simulation(request,net_id):
    if(request.method == 'POST'):
        try:
            iter = json.loads(request.body)['iter']
            blocksExeOrder,cycles = get_execution_order(net_id)
            print(blocksExeOrder,cycles)
            # if(cycles):
            #     print(cycles)
            #     for block in cycles:
            #         print(os.path.join(settings.CIRCULAR_BLOCK_DEPENDENCY_DATA,f"{str(block.network_id.pk)}",f"{str(block.true_LB_id.pk)}",f"{str(block.pk)}.json"))
            #         if(os.path.exists(os.path.join(settings.CIRCULAR_BLOCK_DEPENDENCY_DATA,f"{str(block.network_id.pk)}",f"{str(block.true_LB_id.pk)}",f"{str(block.pk)}.json"))):
            #             params_values_initials = get_initial_inputs_block(block)
            #             true_blocks_out_intials = { 'blockId':block.pk,
            #                                 'blockProxyName':block.proxy_name,
            #                                 'outputs':[] }
            #             print(params_values_initials)
            #             if(params_values_initials):
            #                 if(os.path.exists(os.path.join(settings.BLOCKS_PROCESSING_DATA,'Code','Design',f"{block.true_LB_id.pk}",f"{block.true_LB_id.pk}.py"))):
            #                     spec = importlib.util.spec_from_file_location(f"{str(block.true_LB_id.pk)}.py",os.path.join(settings.BLOCKS_PROCESSING_DATA,'Code','Design',f"{block.true_LB_id.pk}",f"{block.true_LB_id.pk}.py"))
            #                     module = importlib.util.module_from_spec(spec)
            #                     spec.loader.exec_module(module)
            #                     blockOuts = module.execute(params_values_initials)
            #                     true_blocks_out_intials["outputs"].append(blockOuts)
            #                     if(os.path.exists(os.path.join(settings.BLOCK_OUTS,f"{str(block.network_id.pk)}",f"{str(block.true_LB_id.pk)}",f"{block.pk}.json"))):
            #                         with open(os.path.join(settings.BLOCK_OUTS,f"{str(block.network_id.pk)}",f"{str(block.true_LB_id.pk)}",f"{block.pk}.json"),'r') as rp:
            #                             existing_outs = json.load(rp)
            #                             existing_outs['outputs'].append(true_blocks_out_intials['outputs'][0])
            #                         with open(os.path.join(settings.BLOCK_OUTS,f"{str(block.network_id.pk)}",f"{str(block.true_LB_id.pk)}",f"{block.pk}.json"),'w') as wp:
            #                             json.dump(existing_outs,wp,indent=4)
            #                     else:
            #                         os.makedirs(os.path.join(settings.BLOCK_OUTS,f"{str(block.network_id.pk)}",f"{str(block.true_LB_id.pk)}"),exist_ok=True)
            #                         with open(os.path.join(settings.BLOCK_OUTS,f"{str(block.network_id.pk)}",f"{str(block.true_LB_id.pk)}",f"{block.pk}.json"),'w') as wp:
            #                             json.dump(true_blocks_out_intials,wp,indent=4)
            #                 else:
            #                     return JsonResponse({"status":"error",'message':"code not found."})
            #         else:
            #             return JsonResponse({'status':'error','message':f'circular dependency found ({[block.proxy_name for block in cycles]}).'})
                 
            if(len(blocksExeOrder) > 0):
                if(os.path.exists(os.path.join(settings.BLOCK_OUTS,f"{str(net_id)}"))):
                    shutil.rmtree(os.path.join(settings.BLOCK_OUTS,f"{str(net_id)}"))
                n = iter
                for iteration in range(0,n,1):
                    for block in blocksExeOrder:
                        print("Execution Order: ",block)
                        print("Blocks in Cycle: ",cycles)
                        if(block in cycles):
                            print(f"***{block}***")
                            if(os.path.exists(os.path.join(settings.CIRCULAR_BLOCK_DEPENDENCY_DATA,f"{str(block.network_id.pk)}",f"{str(block.true_LB_id.pk)}",f"{str(block.pk)}.json"))):
                                params_values_initials = get_initial_inputs_block(block)
                                true_blocks_out_intials = { 'blockId':block.pk,
                                                'blockProxyName':block.proxy_name,
                                                'outputs':[] }
                                # print(params_values_initials)
                                if(params_values_initials):
                                    if(os.path.exists(os.path.join(settings.BLOCKS_PROCESSING_DATA,'Code','Design',f"{block.true_LB_id.pk}",f"{block.true_LB_id.pk}.py"))):
                                        cycles.remove(block)
                                        spec = importlib.util.spec_from_file_location(f"{str(block.true_LB_id.pk)}.py",os.path.join(settings.BLOCKS_PROCESSING_DATA,'Code','Design',f"{block.true_LB_id.pk}",f"{block.true_LB_id.pk}.py"))
                                        module = importlib.util.module_from_spec(spec)
                                        spec.loader.exec_module(module)
                                        blockOuts = module.execute(params_values_initials)
                                        true_blocks_out_intials["outputs"].append(blockOuts)
                                        if(os.path.exists(os.path.join(settings.BLOCK_OUTS,f"{str(block.network_id.pk)}",f"{str(block.true_LB_id.pk)}",f"{block.pk}.json"))):
                                            with open(os.path.join(settings.BLOCK_OUTS,f"{str(block.network_id.pk)}",f"{str(block.true_LB_id.pk)}",f"{block.pk}.json"),'r') as rp:
                                                existing_outs = json.load(rp)
                                                existing_outs['outputs'].append(true_blocks_out_intials['outputs'][0])
                                            with open(os.path.join(settings.BLOCK_OUTS,f"{str(block.network_id.pk)}",f"{str(block.true_LB_id.pk)}",f"{block.pk}.json"),'w') as wp:
                                                json.dump(existing_outs,wp,indent=4)
                                        else:
                                            os.makedirs(os.path.join(settings.BLOCK_OUTS,f"{str(block.network_id.pk)}",f"{str(block.true_LB_id.pk)}"),exist_ok=True)
                                            with open(os.path.join(settings.BLOCK_OUTS,f"{str(block.network_id.pk)}",f"{str(block.true_LB_id.pk)}",f"{block.pk}.json"),'w') as wp:
                                                json.dump(true_blocks_out_intials,wp,indent=4)
                                    else:
                                        return JsonResponse({"status":"error",'message':"code not found."})
                            else:
                                return JsonResponse({'status':'error','message':f'circular dependency found ({[block.proxy_name for block in cycles]}).'})
                        else:
                            true_blocks_out = { 'blockId':block.pk,
                                                'blockProxyName':block.proxy_name,
                                                'outputs':[] }
                            params_values = get_inputs_block(block,iteration)
                            if(params_values):
                                print(params_values)
                                if(block.network_id.network_type == 'design'):
                                    if(os.path.exists(os.path.join(settings.BLOCKS_PROCESSING_DATA,'Code','Design',f"{block.true_LB_id.pk}",f"{block.true_LB_id.pk}.py"))):
                                        spec = importlib.util.spec_from_file_location(f"{str(block.true_LB_id.pk)}.py",os.path.join(settings.BLOCKS_PROCESSING_DATA,'Code','Design',f"{block.true_LB_id.pk}",f"{block.true_LB_id.pk}.py"))
                                        module = importlib.util.module_from_spec(spec)
                                        spec.loader.exec_module(module)
                                        blockOuts = module.execute(params_values)
                                        true_blocks_out["outputs"].append(blockOuts)
                                        if(os.path.exists(os.path.join(settings.BLOCK_OUTS,f"{str(block.network_id.pk)}",f"{str(block.true_LB_id.pk)}",f"{block.pk}.json"))):
                                            with open(os.path.join(settings.BLOCK_OUTS,f"{str(block.network_id.pk)}",f"{str(block.true_LB_id.pk)}",f"{block.pk}.json"),'r') as rp:
                                                existing_outs = json.load(rp)
                                                existing_outs['outputs'].append(true_blocks_out['outputs'][0])
                                            with open(os.path.join(settings.BLOCK_OUTS,f"{str(block.network_id.pk)}",f"{str(block.true_LB_id.pk)}",f"{block.pk}.json"),'w') as wp:
                                                json.dump(existing_outs,wp,indent=4)
                                        else:
                                            os.makedirs(os.path.join(settings.BLOCK_OUTS,f"{str(block.network_id.pk)}",f"{str(block.true_LB_id.pk)}"),exist_ok=True)
                                            with open(os.path.join(settings.BLOCK_OUTS,f"{str(block.network_id.pk)}",f"{str(block.true_LB_id.pk)}",f"{block.pk}.json"),'w') as wp:
                                                json.dump(true_blocks_out,wp,indent=4)
                                    else:
                                        return JsonResponse({"status":"error",'message':"code not found."})
                                elif(block.network_id.network_type == 'performance'):
                                    pass
                                elif(block.network_id.network_type == 'lifing'):
                                    pass
                                else:
                                    pass
                                # all_blocks_outs['all_blocks_outs'].append(true_blocks_out)
                            else:
                                return ({'status':'error','message':'check inputs outputs and code'})
                        
                all_blocks_outs = get_all_blocks_outputs(net_id)
                return JsonResponse({"status":"success","message":"Blocks Executed Successfully.","res":all_blocks_outs})
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

# def run_simulation(request,net_id):
#     if(request.method == 'GET'):
#         try:
#             blocksExeOrder = get_execution_order(net_id)
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

def make_block_connection(request,net_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            functionSourceId = data['source_id']
            functionDestinationId = data['destination_id']

            functionBlockSourceInstance = functionBlockData.objects.get(pk=functionSourceId)
            functionBlockDestinationInstance = functionBlockData.objects.get(pk=functionDestinationId)
            networkInstance = Network.objects.get(pk=net_id)

            functionConnectionInstance = Connections(source=functionBlockSourceInstance,destination=functionBlockDestinationInstance,network_id = networkInstance)
            functionConnectionInstance.save()
            id = functionConnectionInstance.pk
            
            return JsonResponse({'status':'success','message':'connection inserted sucessfully','id':id})
        except Exception as e:
            print("error"+str(e))
            return JsonResponse({'status':'error','message':'connection not inserted sucessfully'})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def make_block_connection_reconst(request,net_id):
    if(request.method == 'POST'):
        try:
            
            id = json.loads(request.body)['id']
            src_id = json.loads(request.body)['source_id']
            dest_id = json.loads(request.body)['destination_id']

            srcInstance = functionBlockData.objects.get(pk=src_id)
            destInstance = functionBlockData.objects.get(pk=dest_id)
            
            networkInstance = Network.objects.get(pk=net_id)

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
    
def remove_function_block_connection(request,net_id):
    if(request.method == 'POST'):
        connectionId = json.loads(request.body)['connection_id']
        networkInstance = Network.objects.get(pk = net_id)
        connectionInstance = Connections.objects.get(pk = connectionId, network_id = networkInstance)

        destinationInstance = connectionInstance.destination
        destinationTrueId = destinationInstance.true_LB_id.pk
        destinationId = destinationInstance.pk

        sourceInstance = connectionInstance.source
        sourceId = sourceInstance.pk
        sourceProxyName = sourceInstance.proxy_name

        if(os.path.exists(os.path.join(settings.BLOCK_IO,f"{str(net_id)}",f"{str(destinationTrueId)}",f"{str(destinationId)}.json"))):

            with open(os.path.join(settings.BLOCK_IO,f"{str(net_id)}",f"{str(destinationTrueId)}",f"{str(destinationId)}.json"),'r') as rp:
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
            # with open(os.path.join(settings.BLOCK_IO,f"{str(net_id)}",f"{str(destinationTrueId)}",f"{str(destinationId)}.json"),"w") as wp:
            #     json.dump(destinationInputsValuesInstance,wp,indent=4)

            # os.remove(os.path.join(settings.BLOCK_IO,f"{str(net_id)}",f"{str(destinationTrueId)}",f"{str(destinationId)}.json"))
            
            # return JsonResponse({"status":"success","message":"connection and dependent block IO deleted sucessfully"})
        else:
            connectionInstance.delete()
            return JsonResponse({"status":"success","message":"connection deleted sucessfully","remove":True})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def get_dest_block_num_connections(request,net_id):
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
    
def get_conncetion_existence(request,net_id):
    if(request.method == 'POST'):
        blockId = json.loads(request.body)['blockId']
        try:
            functionBlockInstance = functionBlockData.objects.get(network_id=net_id, id=blockId)
            asSourceInstance = Connections.objects.filter(network_id=net_id,source=functionBlockInstance).values()
            asDestinationInstance = Connections.objects.filter(network_id=net_id , destination=functionBlockInstance).values()

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

def get_function_block_dependencies(request,net_id,true_block_id,clone_block_id):
    if(request.method == 'GET'):
        cloneBlockId = clone_block_id
        dependencies = []
        try:

            functionBlockConnectionInstances = Connections.objects.filter(destination = cloneBlockId, network_id = net_id)
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

def clear_all(request,net_id):
    if(request.method == "POST"):
        try:
            refresh = json.loads(request.body)['refresh']
            networkInstance = Network.objects.get(pk=net_id)
            Connections.objects.filter(network_id = networkInstance).delete()
            functionBlockData.objects.filter(network_id = networkInstance).delete()
            if(not refresh):
                if(os.path.exists(os.path.join(settings.BLOCK_IO,f"{str(net_id)}"))):
                    shutil.rmtree(os.path.join(settings.BLOCK_IO,f"{str(net_id)}"))

                if(os.path.exists(os.path.join(settings.BLOCK_OUTS,f"{str(net_id)}"))):
                    shutil.rmtree(os.path.join(settings.BLOCK_OUTS,f"{str(net_id)}"))
                    
                if(os.path.exists(os.path.join(settings.NETWORK_CURRENT_STATE,f"{str(net_id)}"))):
                    shutil.rmtree(os.path.join(settings.NETWORK_CURRENT_STATE,f"{str(net_id)}"))
                
                if(os.path.exists(os.path.join(settings.CIRCULAR_BLOCK_DEPENDENCY_DATA,f"{str(net_id)}"))):
                    shutil.rmtree(os.path.join(settings.CIRCULAR_BLOCK_DEPENDENCY_DATA,f"{str(net_id)}"))
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
def get_block_inputs_populate(request,net_id,true_block_id,clone_block_id):
    if(request.method == 'GET'):
        block_id = true_block_id
        try:
            if(os.path.exists(os.path.join(settings.BLOCK_IO,f"{str(net_id)}",f"{str(true_block_id)}",f"{str(clone_block_id)}.json"))):
                inputsValuesFile = os.path.join(settings.BLOCK_IO,f"{str(net_id)}",f"{str(true_block_id)}",f"{str(clone_block_id)}.json")
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
    
def get_block_initial_inputs_populate(request,net_id,true_block_id,clone_block_id):
    if(request.method == 'GET'):
        block_id = true_block_id
        try:
            if(os.path.exists(os.path.join(settings.CIRCULAR_BLOCK_DEPENDENCY_DATA,f"{str(net_id)}",f"{str(true_block_id)}",f"{str(clone_block_id)}.json"))):
                inputsValuesFile = os.path.join(settings.CIRCULAR_BLOCK_DEPENDENCY_DATA,f"{str(net_id)}",f"{str(true_block_id)}",f"{str(clone_block_id)}.json")
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
    
def go_back_to_home(request,net_id,true_block_id,clone_block_id):
    if(request.method == 'GET'):
        return JsonResponse({"status":"success","url":f"/{net_id}/simulate"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def get_user_inputs_value_url(request,net_id,true_block_id,clone_block_id):
    if(request.method == 'GET'):
        return JsonResponse({"status":"success","url":f"{true_block_id}/{clone_block_id}/block_user_input_value"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    
def block_user_input_value(request,net_id,true_block_id,clone_block_id):
    if(request.method == "GET"):
        return render(request,'user_block_input_value.html')
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
                return redirect('index')  # Success login
            else:
                messages.error(request, "Access denied: You are not authorized to log in here.")
        else:
            messages.error(request, "Invalid username or password.")
        
        # Return to landing page in both failure cases
        return render(request, 'landingpage.html')

    # For GET request show login page (e.g., index)
    return render(request, 'index.html')


def Admin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Check if user is in the 'Simulation user' group
            if user.groups.filter(name='Admin').exists():
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



@login_required
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
        user = User.objects.get(id=user_id)

        # Clear previous settings
        UserModuleAccess.objects.filter(user=user).delete()
        UserSubmoduleAccess.objects.filter(user=user).delete()

        # Save selected modules (ensure modules are added when submodules are selected)
        selected_modules = request.POST.getlist("modules")
        for module_name in selected_modules:
            module = Modules.objects.get(id=module_name)
            UserModuleAccess.objects.create(user=user, module=module)

        # Save selected submodules
        selected_submodules = request.POST.getlist("submodules")
        for submodule_name in selected_submodules:
            submodule = SubModules.objects.get(id=submodule_name)
            UserSubmoduleAccess.objects.create(user=user, submodule=submodule)

            # Ensure the module associated with the submodule is also selected
            module = submodule.module  # Get the module related to the submodule
            if not UserModuleAccess.objects.filter(user=user, module=module).exists():
                UserModuleAccess.objects.create(user=user, module=module)

        return redirect('developer_dashboard')
    
    