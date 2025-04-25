def execute(inputs):
    bod_load_kg_day = round((inputs['Flow(kld)']*inputs['BOD_in(mg/l)'])/1000,3)
    oxy_req_kg_day = bod_load_kg_day * inputs['Oxygen_Required_for_1_kg_BOD_removal(kg/day)']
    air_req_cum_d = round(oxy_req_kg_day/(0.21*1.2*0.6*0.9*0.25),3)
    air_req_mix_cum_hr = round(air_req_cum_d/24,3)
    provide_membrance_diffuser_aeriation_tank_no = round(inputs['Actual_requirement_of_air(cum/hr)']/inputs['Fine_bubble_diffuser_assumed_to_inject_oxygen_of(cum/hr)'],3) 
    each_blower_cap_nil = round(inputs['Actual_requirement_of_air(cum/hr)']/inputs['No._of_working_blowers(nil)'],3)

    outputs = {
        "BoD_load(kg/day)":bod_load_kg_day,
        "Oxygen_Required(kg/day)":oxy_req_kg_day,
        "Air_required(cum/d)":air_req_cum_d,
        "Air_requirement_for_mixing(cum/hr)":air_req_mix_cum_hr,
        "Provide_Membrance_diffuser_for_aeration_tank(No.)":provide_membrance_diffuser_aeriation_tank_no,
        "Each_Blower_capacity(nil)":each_blower_cap_nil
    }

    return outputs