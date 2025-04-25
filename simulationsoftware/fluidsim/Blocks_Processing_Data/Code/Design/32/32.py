import math

def execute(inputs):

    Peak_Sewage_flow_entering=inputs['Assumed_Peak_Factor(nil)']*inputs['Average_Sewage_flow_entering(KLD)']

    

    outputs = {

        'Peak_Sewage_flow_entering(KLD)':Peak_Sewage_flow_entering

    }

    return outputs