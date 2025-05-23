def execute(inputs):

    flow_m3_hr = round(inputs['Flow(kld)']/24,3)

    bod_load_kg_d = round((inputs['Flow(kld)']*inputs['BOD_in(mg/l)'])/1000,3)

    bod_out_mg_l = round(inputs['BOD_in(mg/l)']-((inputs['BOD_removal(%)']/100)*inputs['BOD_in(mg/l)']),3)

    area_per_piece_m2 = round(inputs['surface_area_of_MBBR_media(m2/m3)']/inputs['no_of_pieces_per_cum(per_m3)'],3)

    psa_tsa_nil = round(inputs['protected_surafe_area(m2/m3)']/inputs['surface_area_of_MBBR_media(m2/m3)'],3)

    media_req_m3 = round(bod_load_kg_d/inputs['Loading_rates(kg_BOD/m3.d)'],3)

    tank_volume_m3 = round(media_req_m3/(inputs['fill_range_of_media_percent(%)']/100),3)

    hrt_hrs = round(tank_volume_m3/(inputs['Flow(kld)']/24),3)

    tank_volume_m3_1 = round(inputs['adopting_a_HRT(hrs)']*(inputs['Flow(kld)']/24),3)

    per_fill_achieved_percent = round((media_req_m3/tank_volume_m3_1)*100,3)



    outputs = {

        'flow(m3/hr)':flow_m3_hr,

        'BOD_load(kg/d)':bod_load_kg_d,

        'BOD_out(mg/l)':bod_out_mg_l,

        'area_per_piece(m2)':area_per_piece_m2,

        'PSA_TSA(nil)':psa_tsa_nil,

        'Media_required(m3)':media_req_m3,

        'tank_volume(m3)':tank_volume_m3,

        'tank_volume_1(m3)':tank_volume_m3_1,

        'HRT_hrs(nil)':hrt_hrs,

        'Percent_fill_achieved_percent(%)':per_fill_achieved_percent 

    }



    return outputs