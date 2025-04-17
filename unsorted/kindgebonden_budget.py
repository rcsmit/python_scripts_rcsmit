
def calculate_kindgebonden_budget(inkomen, toeslagpartner,aantal_kinderen, aantal_kinderen_12_15, aantal_kinderen_16_17):
    """_summary_

    Args:
        inkomen (int): Totaal belastbaar inkomen per jaar
        toeslagpartner (boolean): Is er een toeslagpartner
        aantal_kinderen (int): aantal kinderen onder de 18 totaal
        aantal_kinderen_12_15 (int): aantal kinderen 12 tot en met 15
        aantal_kinderen_16_17 (int): aantal kinderen 16 of 17 jaar

    Returns:
        int: Bedrag kindgebonden budget per jaar
    """    
    # https://download.belastingdienst.nl/toeslagen/docs/berekening_kindgebonden_budget_tg0811z21fd.pdf
    # geen toeslagpartner
    #     
    if aantal_kinderen == 0:
        kindgebonden_budget = 0
    else:
        if aantal_kinderen < aantal_kinderen_12_15+aantal_kinderen_16_17:
            raise Exception ("Aantal kinderen klopt niet")
        if toeslagpartner == False:
            if aantal_kinderen == 1: maximaal_bedrag_kindgebonden_budget = 4505
            if aantal_kinderen == 2: maximaal_bedrag_kindgebonden_budget = 5611
            if aantal_kinderen == 3: maximaal_bedrag_kindgebonden_budget = 6612
            if aantal_kinderen >= 4: maximaal_bedrag_kindgebonden_budget = 6612 + (aantal_kinderen-3)*1001
        else:
            if aantal_kinderen == 1: maximaal_bedrag_kindgebonden_budget = 1220
            if aantal_kinderen == 2: maximaal_bedrag_kindgebonden_budget = 2326
            if aantal_kinderen == 3: maximaal_bedrag_kindgebonden_budget = 3327
            if aantal_kinderen >= 4: maximaal_bedrag_kindgebonden_budget = 6612 + (aantal_kinderen-3)*1001
        
        maximaal_bedrag_kindgebonden_budget = maximaal_bedrag_kindgebonden_budget + (251*aantal_kinderen_12_15)
        maximaal_bedrag_kindgebonden_budget = maximaal_bedrag_kindgebonden_budget + (447*aantal_kinderen_16_17)
        
        if toeslagpartner == False:
            if inkomen > 22356:
                vermindering =  0.0675 * (inkomen - 22356)
                kindgebonden_budget = maximaal_bedrag_kindgebonden_budget - vermindering
            else:
                kindgebonden_budget = maximaal_bedrag_kindgebonden_budget
        else:
            if inkomen > 39596:
                vermindering =  0.0675 * (inkomen - 39596)
                kindgebonden_budget = maximaal_bedrag_kindgebonden_budget - vermindering
            else:
                kindgebonden_budget = maximaal_bedrag_kindgebonden_budget

    return kindgebonden_budget

kindgebonden_budget = calculate_kindgebonden_budget(25000,False,1,4,0)
print (kindgebonden_budget)