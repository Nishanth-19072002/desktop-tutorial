def execute(inputs):
    concentration_mg_l = inputs['Concentration(%)'] * 10000
    dosing_volume_day_cum_d = round((inputs['Flow_rate(KLD)'] * inputs['Dosage(mg/l)'])/concentration_mg_l,3)
    dosing_cap_LPH = round((dosing_volume_day_cum_d*1000)/inputs['Working_hours_per_day(hrs)'],3)

    outputs={
        'Concentration(mg/l)':concentration_mg_l,
        'Dosing_volume_per_day(cum/d)':dosing_volume_day_cum_d,
        'Dosing_capacity(LPH)':dosing_cap_LPH
    }

    return outputs