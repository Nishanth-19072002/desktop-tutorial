import math



def execute(inputs):

    total_cycle_time=inputs['Time_for_Fill_Aerate_phase_provided(h)']+inputs['Time_for_Settle_phase_provided(h)']+inputs['Time_for_Decant_phase_provided(h)']

    flow_rate=inputs['Q_per_tank(cum/day)']/24

    flow_rate_each_basin=flow_rate/inputs['No_of_Basins_under_Fill_simultaneously(No)']

    mlvss=inputs['MLSS_considered(mg/l)']*0.8

    total_volume_of_area_basin=inputs['Q_per_tank(cum/day)'] * inputs['Inlet_BOD(mg/l)'] / (mlvss * inputs['F/M(nil)'])

    volume_reqd_per_basin=total_volume_of_area_basin/inputs['No_of_Tanks(Nos)']

    area_of_each_basin=volume_reqd_per_basin/inputs['Side_Water_Depth_Assume(m)']

    width_assume=math.sqrt(area_of_each_basin)

    length=area_of_each_basin/width_assume

    total_depth=inputs['Freeboard(m)']+inputs['Side_Water_Depth_Assume(m)']

    hydraulic_retention_time=volume_reqd_per_basin *24/inputs['Q_per_tank(cum/day)']

    solid_retention_time=total_volume_of_area_basin*inputs['MLSS_considered(mg/l)']/(0.00044*1000)

    recirculation_flow=flow_rate_each_basin*inputs['Recirculation_Ratio(%)']/100

    design_flow=flow_rate_each_basin+recirculation_flow

    volume_reqd=design_flow*inputs['Hydraulic_Retention_Time_HRT_DesignFlow(min)']/60

    width_reqd=volume_reqd/(inputs['Side_Water_Depth_provided(m)']*inputs['Length(m)'])

    Bod_removed=inputs['Inlet_BOD(mg/l)'] - inputs['Outlet_BOD(mg/l)']

    bod_removed_in_a_day=Bod_removed*inputs['Q_per_tank(cum/day)']/1000

    o2_reqd_for_oxid_bod=bod_removed_in_a_day*inputs['O2_required_for_oxidation_of_BOD(Kg/Kg)']

    nitrogen_assimilated_during_oxidationofbod=(Bod_removed*5)/100

    NH3_nitrified_in_a_day=inputs['Inlet_TKN(mg/l)'] - inputs['Outlet_NH3_N(mg/l)'] - nitrogen_assimilated_during_oxidationofbod

    NH3_nitrified_in_a_day_kgd=inputs['Q_per_tank(cum/day)']*NH3_nitrified_in_a_day/1000

    o2_reqd_for_nitrification_of_nh3n=NH3_nitrified_in_a_day_kgd * inputs['O2_required_for_nitrification_of_NH3_N(Kg/NH3_N)']

    no3n_reqd_for_nitrification=(NH3_nitrified_in_a_day*75)/100

    no3n_denitrified=no3n_reqd_for_nitrification - inputs['Outlet_NO3_N(mg/l)']

    amount_of_no3_denitrified=no3n_denitrified*inputs['Q_per_tank(cum/day)']/1000

    o2_credit_available=amount_of_no3_denitrified * inputs['O2_credit_during_de_nitrification_of_NO3_N(Kg/Kg)']

    o2_credit_to_be_considered=(o2_credit_available*inputs['O2_credit_to_be_considered_during_de_nitrification(%)'])/100

    total_o2_including_o2_denitrification=o2_reqd_for_oxid_bod + o2_reqd_for_nitrification_of_nh3n - o2_credit_to_be_considered

    T_temperature=inputs['T(C)']+273

    hencec5th=inputs['CST_Oxygen_Saturation_Concentration_in_Clean_Water_at_Temperature_T(mg/l)']*math.exp( - (inputs['g(m/s2)']*inputs['M(Kg/Kg_mole)']*(inputs['zb(m)']-inputs['za(m)']))/(inputs['R(Nm/Kg_mole.K)']*T_temperature))

    t_temp=hencec5th+273

    hence_patm=inputs['Pa(mWC)']*math.exp( - (inputs['g1(m/s2)'] * inputs['M1(Kg/Kg_mole)'] * (inputs['zb1(m)'] - inputs['za1(m)']))/(inputs['R1(Nm/Kg_mole.K)'] * t_temp))

    pd_pressure_at_depth_of=hence_patm + (inputs['Side_Water_Depth_Assume(m)'] -  1)

    hence_c1sth=hencec5th * (1/2) * ((pd_pressure_at_depth_of / hence_patm) + (inputs['Ot(nil)'] / 21))

    SOTR = inputs['Actual_Oxygen_Transfer_Rate_AOTR_under_field_conditions(kg/d)'] / ((((inputs['beta(nil)'] * hence_c1sth) - inputs['CL:(mg/l)']) / inputs['CS20:_Dissolved_Oxygen(mg/l)']) *(1.024 ** (inputs['T(C)'] - 20)) *inputs['alpha(nil)'] *inputs['F(nil)'])


    standard_o2_reqd_at_field=SOTR / inputs['No_of_Tanks(Nos)']

    effective_areation_depth=inputs['Aeration_Depth(m)'] -  inputs['Height_at_which_Diffusers_are_kept(m)']

    air_reqd_at_fields_conds=standard_o2_reqd_at_field / (inputs['SOTE(%)'] /100  * inputs['Fraction_of_O2_in_Air(%)'] /100 * inputs['Specific_Gravity_of_Air_at_Standard_Condition(nil)'])

    air_reqd_perhour_perbasin=air_reqd_at_fields_conds / inputs['Hours_of_Aeration_per_Basin_perday(hr/d/basin)']

    capacity_of_air_blowers=air_reqd_perhour_perbasin / inputs['No_of_Operating_Air_Blowers_perBasin(Nos.)']





    outputs={

        'Total_Cycle_Time_provided(h)':total_cycle_time,

        'Flow_Rate(cum/h)':flow_rate,

        'Flow_Rate_through_each_basin(cum/h)':flow_rate_each_basin,

        'MLVSS(mg/l)':mlvss,

        'Total_Volume_of_Aeration_Basins(cum)': total_volume_of_area_basin,

        'Volume_required_perBasin(cum)':volume_reqd_per_basin,

        'Area_of_each_basin(m2)':area_of_each_basin,

        'Width_Assume(m)':width_assume,

        'Length(m)':length,

        'Total_Depth(m)':total_depth,

        'BOD_removed_in_a_day(kg/d)':bod_removed_in_a_day,

        'O2_required_for_oxidation_of_BOD(kg/d)':o2_reqd_for_oxid_bod,

        'Hydraulic_Retention_Time(h)':hydraulic_retention_time,

        'Solids_Retention_Time(nil)':solid_retention_time,

        'Recirculation_Flow(m3/h)':recirculation_flow,

        'Design_Flow(m3/h)':design_flow,

        'Volume_required(m3)':volume_reqd,

        'Width_required(m)':width_reqd,

        'BOD_removed(mg/l)':Bod_removed,

        'Nitrogen_assimilated_during_oxidation_of_BOD(mg/l)':nitrogen_assimilated_during_oxidationofbod,

        'NH3_N_nitrified_in_a_day(mg/l)':NH3_nitrified_in_a_day,

        'O2_required_for_nitrification_of_NH3_N(kg/d)':o2_reqd_for_nitrification_of_nh3n,

        'NO3_N_generated_assuming_75%_nitrification_of_NH3_N(mg/l)':no3n_reqd_for_nitrification,

        'NO3_N_that_is_denitrified(mg/l)':no3n_denitrified,

        'Amount_of_NO3_N_that_is_denitrified(kg/d)':amount_of_no3_denitrified,

        'O2_credit_available_during_de_nitrification(kg/d)':o2_credit_available,

        'O2_credit_to_be_considered_during_de_nitrification(kg/d)':o2_credit_to_be_considered,

        'Total_O2_required_including_O2_credit_during_denitrification(kg/d)':total_o2_including_o2_denitrification,

        'T(K)':T_temperature,

        'Hence_CSTH(mg/l)':hencec5th,

        'T1(K)':t_temp,

        'Hence_Patm_H(nil)':hence_patm,

        'Air_required_per_hour_perBasin(Nm3/hr/Basin)':air_reqd_perhour_perbasin,

        'Capacity_of_Air_Blowers_required(Nm3/hr/Basin)':capacity_of_air_blowers,

        'NH3_N_nitrified_in_a_day(kg/d)':NH3_nitrified_in_a_day_kgd,

        'Pd_Pressure_at_the_Depth_of_Air_Release(mWC)':pd_pressure_at_depth_of,

        'Effective_Aeration_Depth(m)':effective_areation_depth,

        'Air_required_at_Field_Conditions_perBasin(Nm3/day/Basin)':air_reqd_at_fields_conds,

        'Standard_O2_required_at_Field_Conditions_perBasin(kg/d/Basin)':standard_o2_reqd_at_field,

        'SOTR(kg/d)':SOTR,

        'Hence_C1STH(mg/l)':hence_c1sth,

        



    }

    return outputs