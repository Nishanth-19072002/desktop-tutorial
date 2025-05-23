import os
import shutil
from django.conf import settings
import json
def get_all_blocks_outputs(net_id):
    all_block_out = {'all_blocks_outs':[]}
    if(os.path.exists(os.path.join(settings.BLOCK_OUTS,f"{str(net_id)}"))):
        true_block_ids = os.listdir(os.path.join(settings.BLOCK_OUTS,f"{str(net_id)}"))
        for true_id in true_block_ids:
            clone_ids = os.listdir(os.path.join(settings.BLOCK_OUTS,f"{str(net_id)}",f"{str(true_id)}"))
            for clone_id in clone_ids:
                if(clone_id.endswith(".json")):
                    with open(os.path.join(settings.BLOCK_OUTS,f"{str(net_id)}",f"{str(true_id)}",f"{str(clone_id)}"),'r') as rp:
                        outputs = json.load(rp)
                        all_block_out['all_blocks_outs'].append(outputs)
                else:
                    return False
        return all_block_out
    else:
        return False
                      