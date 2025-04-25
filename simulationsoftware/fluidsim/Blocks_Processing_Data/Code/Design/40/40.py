import math

def execute(inputs):
    excess_sludge_to_be_wasted=inputs['Volume_of_Sludge_to_be_Wasted_perCycle(m3)']*inputs['No_of_Basins_provided(Nos)']
    volume_of_sludge_handling=excess_sludge_to_be_wasted*inputs['Holding_time(h)']
    area_of_the_tank=volume_of_sludge_handling/inputs['Depth_of_tank(m)']
    forsquare_tank_length=math.sqrt(area_of_the_tank)

    outputs={
        'Excess_sludge_to_be_wasted(KLD)':excess_sludge_to_be_wasted,
        'Volume_of_sludge_holding_tank(cum)':volume_of_sludge_handling,
        'Area_of_the_tank(m)':area_of_the_tank,
        'forsquare_tank_length(m)':forsquare_tank_length
    }
    return outputs