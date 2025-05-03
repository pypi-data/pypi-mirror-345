__standards = [

    'standard-ASTM-D7078'
    ,'standard-ASTM-D7264'
    ,'standard-ASTM-D3039'
    ,'standard-ASTM-D638'

]

def get_standards()->list[str]:
    """Helper function to retrive of possible standards"""
    return __standards

def print_standards():
    '''
    Prints the avaliable standards:
    '''
    for each_s in __standards:
        print(f'''
=======================================
STANDARD_NAME : {each_s}
=======================================
''')
