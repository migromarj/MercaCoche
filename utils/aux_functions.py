import unidecode

def unidecode_values(province, fuel, color):

    if province != None:
        province = unidecode.unidecode(province).lower()
    if fuel != None:
        fuel = unidecode.unidecode(fuel).lower()
    if color != None:
        color = unidecode.unidecode(color).lower()

    return province, fuel, color