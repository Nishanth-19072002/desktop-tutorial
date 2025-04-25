def execute(inputs):

    design_bod_rem_kg_day = round((inputs['Average_daily_flow(Cum/day)'] * inputs['BOD(mg/Lt)']) / 1000,3)

    excess_sludge_produced_kg_day = design_bod_rem_kg_day*0.25

    slurry_volume_lts = round((excess_sludge_produced_kg_day*100)/inputs['Slurry_Consistency(%)'],3)

    sludge_cake_volume_lts = round(excess_sludge_produced_kg_day/inputs['Proportion_of_solids_in_cake(nil)'],3)

    num_plates_nos = round(inputs['Cake-holding_capacity_of_filter_press(Litres)']/inputs['Capcity_of_per_chamber(lit/chamber)'],3)



    outputs = {

        'Design_BOD_Removal(kg/day)':design_bod_rem_kg_day,

        'Excess_Sludge_Produced(kg/day)':excess_sludge_produced_kg_day,

        'Slurry_Volume(Litres)' : slurry_volume_lts,

        'Sludge_cake_volume(Litres)':sludge_cake_volume_lts,

        'Number_of_Plates(nos)':num_plates_nos

    }



    return outputs