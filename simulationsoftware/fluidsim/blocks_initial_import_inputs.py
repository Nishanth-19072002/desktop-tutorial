import os
from django.conf import settings
import json
import pandas as pd
from fluidsim.models import *

def get_initial_inputs_block(block):
    cloneBlockId = block.pk
    trueBlockId = block.true_LB_id.pk
    networkId = block.network_id.pk
    try:
        user_inputs_path = os.path.join(settings.CIRCULAR_BLOCK_DEPENDENCY_DATA,f"{str(networkId)}",f"{str(trueBlockId)}",f"{str(cloneBlockId)}.json")
        if(os.path.exists(user_inputs_path)):
            with open(user_inputs_path,"r") as rp:
                file = json.load(rp)
            inputs_values = {}

            for input_value in file['inputs_values']:
                if(input_value['val_from'] == 'excel'):
                    if(os.path.exists(os.path.join(settings.NETWORK_INPUT_FILES,f"{str(networkId)}",f"{input_value['excel_file']}"))):
                        if(input_value['excel_file'].endswith('.csv')):
                            df_csv = pd.read_csv(os.path.join(settings.NETWORK_INPUT_FILES,f"{str(networkId)}",f"{input_value['excel_file']}"))
                            inputs_values[f"{input_value['param_name']}({input_value['unit']})"] = df_csv[f"{input_value['excel_column']}"].values.tolist()[0]
                        else:
                            df_excel = pd.read_excel(os.path.join(settings.NETWORK_INPUT_FILES,f"{str(networkId)}",f"{input_value['excel_file']}"),engine='openpyxl')
                            inputs_values[f"{input_value['param_name']}({input_value['unit']})"] = df_excel[f"{input_value['excel_column']}"].values.tolist()[0]
                # elif(input_value['val_from'] == 'previous'):
                #     try:
                #         previousBlockInstance = functionBlockData.objects.get(pk=input_value["previous_block"],network_id=networkId)
                #         preNetInstance = previousBlockInstance.network_id
                #         preTrueInstance = previousBlockInstance.true_LB_id
                #         preOutsInstance = LogicBlockDesignOutputs.objects.get(pk=input_value['previous_block_output'],LB_id=preTrueInstance)
                #         preOutName = f"{preOutsInstance.out_param_name}({preOutsInstance.unit})"
                #         if(os.path.exists(os.path.join(settings.BLOCK_OUTS,f"{str(preNetInstance.pk)}",f"{str(preTrueInstance.pk)}",f"{str(input_value["previous_block"])}.json"))):
                #             with open(os.path.join(settings.BLOCK_OUTS,f"{str(preNetInstance.pk)}",f"{str(preTrueInstance.pk)}",f"{str(input_value["previous_block"])}.json"),'r') as rp:
                #                 outs = json.load(rp)
                #                 inputs_values[f"{input_value['param_name']}({input_value['unit']})"] = outs['outputs'][iteration][preOutName]
                #         else:
                #             print("no inputs")
                #             return False
                #     except Exception as e:
                #         print(e)
                else:
                    return False
            
            return inputs_values
        else:
            return False
    except Exception as e:
        print(f"from_initial_import_inputs.py-{e}")
        return False