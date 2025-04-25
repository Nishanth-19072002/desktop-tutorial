import math

def execute(inputs):

    sludge_prod_per_day_KLD = round((inputs['Average_Sewage_flow_entering_the_treatment_plant(KLD)'] * inputs['BOD(mg/Lt)'])/10000,3)

    excess_sludge_wasted_KLD = round((sludge_prod_per_day_KLD * inputs['Sludge_to_be_wasted(%)'])/100,3)

    volume_sludge_holding_tank_cum = excess_sludge_wasted_KLD * inputs['Holding_time(h)']

    area_of_tank_sqm = round(volume_sludge_holding_tank_cum/inputs['Depth_of_tank(m)'],3)

    sq_tank_length_m = round(math.sqrt(area_of_tank_sqm),3)

    width_m = sq_tank_length_m



    outputs={

        "Sludge_Produced_Per_day(KLD)":sludge_prod_per_day_KLD,

        "Excess_sludge_to_be_wasted(KLD)":excess_sludge_wasted_KLD,

        "Volume_of_sludge_holding_tank(cum)":volume_sludge_holding_tank_cum,

        "Area_of_the_tank(sqm)":area_of_tank_sqm,

        "For_square_tank,_Length(m)":sq_tank_length_m,

        "Width(m)":width_m

    }

    

    return outputs