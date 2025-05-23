import math

def execute(inputs):
    Excess_sludge_to_be_wasted=inputs['BOD(kg/d)']*inputs['Specific_Sludge_Yield(Kg/Kg)']
    sludge_to_be_wasted_per_basin=Excess_sludge_to_be_wasted/inputs['No_of_Basins_provided(Nos)']
    sludge_wasted_percycle_perbasin=sludge_to_be_wasted_per_basin/inputs['No_of_Cycles(Nos)']
    solids_consistency = inputs['Solids_Consistency_in_the_Wasted_Sludge(%)'] / 100  # e.g., 0.6% becomes 0.006
    volume_of_sludge_to_be_wasted = sludge_wasted_percycle_perbasin / (solids_consistency * 1000)
    cpacity_of_sas_pump=volume_of_sludge_to_be_wasted*60/inputs['Considering_Running-Time_of_Surplus_Activated_Sludge(min)']

    outputs={
        'Excess_sludge_to_be_wasted(kg/d)':Excess_sludge_to_be_wasted,
        'Sludge_to_be_Wasted_per_Basin(kg/d)':sludge_to_be_wasted_per_basin,
        'Sludge_to_be_Wasted_per_Cycle_per_Basin(kg/d)':sludge_wasted_percycle_perbasin,
        'Volume_of_Sludge_to_be_Wasted_perCycle(m3)':volume_of_sludge_to_be_wasted,
        'Capacity_of_SAS_Pump_required(cum/h)':cpacity_of_sas_pump
    }
    return outputs
