class _alpha():
    def __init__(self) -> None:

        self.colunas  = [
                             r'Time'
                            ,r'Deslocamento [mm]'
                            ,r'Força'
                            ,r'Tensão à tração'
                            ,r'Deformação à tração (Deslocamento)'
                            ,r'Strain Gauge 1/Axial Strain' # Deformação axial
                            ,r'Strain Gauge 1/Transverse Strain' # Deformação transversal
                            ,r'Strain Gauge 1/Shear Strain' # Deformação cisalhante
                            ,r'Strain Gauge 1/Minimum Normal Strain' # Deformação mínima local
                            ,r'Strain Gauge 1/Maximum Normal Strain' # Deformação máxima local
                            ,r'Strain Gauge 1/Poissons Ratio' # Razao de Poisson
                            ,r'Strain Gauge 1/Axial Displacement' # Deslocamento axial
                            ,r'Strain Gauge 1/Transverse Displacement' # Deslocamento transversal
                         ]

        self.column_delimitador = ','
        self.decimal = '.'
        self.testType = ['tensile']


class _beta():
    def __init__(self) -> None:

        self.colunas  = [
                             r'Tempo'
                            ,r'Deslocamento [mm]'
                            ,r'Força'
                            ,r'Tensão à tração'
                            ,r'Deformação à tração (Deslocamento)'
                            ,r'Extens Bi Axial - Connector 6'
                            ,r'Extens Bi Trans - Conector 5'
                         ]
        self.column_delimitador = ';'
        self.decimal = ','
        self.skip_rows = 18
        self.testType = ['tensile','flexural']



class _gamma():
    def __init__(self) -> None:

        self.colunas  = [
                             r'Tempo'
                            ,r'Deslocamento [mm]'
                            ,r'Força'
                            ,r'Tensão à tração'
                            ,r'Deformação à tração (Deslocamento)'
                            ,r'Deformação digital 1'
                         ]
        self.column_delimitador = ';'
        self.decimal = ','
        self.testType = ['tensile']


class _delta():
    def __init__(self) -> None:

        self.colunas  = [
                             r'Tempo'
                            ,r'Deslocamento [mm]'
                            ,r'Força'
                            ,r'Tensão à tração'
                            ,r'Deformação à tração (Deslocamento)'
                         ]
        self.column_delimitador = ';'
        self.decimal = ','
        self.testType = ['tensile']

class _epsilon():
    def __init__(self) -> None:

        self.colunas  = ['Tempo','Deslocamento','Força','Extensometro']
        self.column_delimitador = ';'
        self.decimal = ','
        self.testType = ['tensile'] # Array com tipos de testes utilizados

class _zeta():
    def __init__(self) -> None:

        self.colunas  = [
                             r'Time measurement'
                            ,r'Extension'
                            ,r'Primary load measurement'
                            ,r'W-E401'
                            ,r'Deformação à flexão (W-E401)'
                            ,r'Deslocamento à flexão'
                            ,r'Tensão à flexão'
        ]
        self.column_delimitador = ';'
        self.decimal = ','
        self.skip_rows = 18
        self.testType = ['flexural'] # Array com tipos de testes utilizados



class _eta():
    def __init__(self) -> None:

        self.colunas  = [
                             r'Time'
                            ,r'Deslocamento [mm]'
                            ,r'Força'
                            ,r'Tensão à tração'
                            ,r'Deformação à tração (Deslocamento)'
                            ,r'Strain Gauge 1/Axial Strain' # Deformação axial
                            ,r'Strain Gauge 1/Transverse Strain' # Deformação transversal
                            ,r'Strain Gauge 1/Shear Strain' # Deformação cisalhante
                            ,r'Strain Gauge 1/Minimum Normal Strain' # Deformação mínima local
                            ,r'Strain Gauge 1/Maximum Normal Strain' # Deformação máxima local
                            ,r'Strain Gauge 1/Poissons Ratio' # Razao de Poisson
                            ,r'Strain Gauge 1/Axial Displacement' # Deslocamento axial
                            ,r'Strain Gauge 1/Transverse Displacement' # Deslocamento transversal
                         ]

        self.column_delimitador = ','
        self.decimal = '.'
        self.testType = ['shear'] # Array com tipos de testes utilizados


class _omicron():
    def __init__(self) -> None:

        self.colunas  = [
                            r'Time',
                            r'Deslocamento',
                            r'Força',
                            r'Tensão ao cisalhamento',
                            r'Deformação ao cisalhamento (Deslocamento)',
                            r'Extensometer 1/Engineering Strain',
                            r'Extensometer 1/True Strain',
                            r'Extensometer 1/Distance Change L(t)-L0',
                            r'Extensometer 1/Distance L(t)',
                            r'Extensometer 2/Engineering Strain',
                            r'Extensometer 2/True Strain',
                            r'Extensometer 2/Distance Change L(t)-L0',
                            r'Extensometer 2/Distance L(t)'
                         ]

        self.column_delimitador = ','
        self.decimal = '.'
        self.skip_rows = 100
        self.testType = ['shear'] # Array com tipos de testes utilizados


class _pi():
    def __init__(self) -> None:

        self.colunas  = [
                             r'Tempo'
                            ,r'Deslocamento'
                            ,r'Força'
                            ,r'Deformação à compressão (Deslocamento)'
                            ,r'Tensão à compressão'
                         ]

        self.column_delimitador = ';'
        self.decimal = ','
        self.skip_rows = 10
        self.testType = ['compression'] # Array com tipos de testes utilizados



class _rho():
    def __init__(self) -> None:

        self.colunas  = [
                             r'Tempo'
                             ,r'Deslocamento'
                            ,r'Força'
                            ,r'Tensão à tração'
                            ,r'Extens Bi Axial - Connector 6'
                            ,r'Extens Bi Trans - Conector 5'
                            ,r'Deformação à tração (Extens Bi Axial - Connector 6)'
                         ]

        self.column_delimitador = ';'
        self.decimal = ','
        self.skip_rows = 30
        self.testType = ['tensile'] # Array com tipos de testes utilizados

class _sigma():
    def __init__(self) -> None:

        self.colunas  = [
                            r"Time",
                            r"Deslocamento",
                            r"Força",
                            r"Tensão à tração",
                            r"Deformação à tração (Deslocamento)",
                            r"Strain Gauge 1/Axial Strain",
                            r"Strain Gauge 1/Transverse Strain",
                            r"Strain Gauge 1/Shear Strain",
                            r"Strain Gauge 1/Minimum Normal Strain",
                            r"Strain Gauge 1/Maximum Normal Strain",
                            r"Strain Gauge 1/Poisson's Ratio",
                            r"Strain Gauge 1/Axial Displacement",
                            r"Strain Gauge 1/Transverse Displacement",
                            r"Extensometer 1/Engineering Strain",
                            r"Extensometer 1/True Strain",
                            r"Extensometer 1/Distance Change L(t)-L0",
                            r"Extensometer 1/Distance L(t)"
                         ]

        self.column_delimitador = ','
        self.decimal = '.'
        self.skip_rows = 100
        self.testType = ['tensile'] # Array com tipos de testes utilizados

class _tau():
    def __init__(self):

        self.colunas = [
                     r'Tempo'
                    ,r'Deslocamento'
                    ,r'Deslocamento à compressão'
                    ,r'Força'
                    ,r'Deformação à compressão (Deslocamento)'
                    ,r'Tensão à compressão'
        ]
        self.column_delimitador = ';'
        self.decimal = ','
        self.skip_rows = 5
        self.testType = ['compression'] # Array com tipos de testes utilizados

class _upsilon():
    def __init__(self):

        self.colunas = [
                 r"Time"
                ,r"Deslocamento"
                ,r"Força"
                ,r"Tensão à tração"
                ,r"Deformação à tração (Deslocamento)"
                ,r"Strain Gauge 1/Axial Strain Ɛyy"
                ,r"Strain Gauge 1/Transverse Strain Ɛxx,"
                ,r"Strain Gauge 1/Shear Strain Ɛxy"
                ,r"Strain Gauge 1/Minimum Normal Strain"
                ,r"Strain Gauge 1/Maximum Normal Strain"
                ,r"Strain Gauge 1/Poisson's Ratio -Ɛxx/Ɛyy"
                ,r"Strain Gauge 1/Axial Displacement dy"
                ,r"Strain Gauge 1/Transverse Displacement dx"
                ,r"Extensometer 1/Engineering Strain"
                ,r"Extensometer 1/True Strain"
                ,r"Extensometer 1/Distance Change L(t)-L0"
                ,r"Extensometer 1/Distance L(t)"
                ,r"Extensometer 2/Engineering Strain"
                ,r"Extensometer 2/True Strain"
                ,r"Extensometer 2/Distance Change L(t)-L0"
                ,r"Extensometer 2/Distance L(t)"
        ]
        self.column_delimitador = ','
        self.decimal = '.'
        self.skip_rows = 5
        self.testType = ['tensile'] # Array com tipos de testes utilizados

class _phi():
    def __init__(self) -> None:

        self.colunas  = [
                             r'Tempo'
                            ,r'Deslocamento'
                            ,r'Deslocamento'
                            ,r'Força'
                            ,r'Deformação à compressão (Deslocamento)'
                            ,r'Tensão à compressão'
                         ]

        self.column_delimitador = ';'
        self.decimal = ','
        self.skip_rows = 10
        self.testType = ['compression'] # Array com tipos de testes utilizados

class _chi():
    def __init__(self) -> None:

        self.colunas  = [
                        r'Test time',
                        r'Temperature',
                        r'Flexure angle',
                        r'Deformation',
                        r'Standard force',
                        r'deflection',
                        r'force',
                         ]

        self.column_delimitador = ','
        self.decimal = '.'
        self.skip_rows = 4
        self.testType = ['flexural'] # Array com tipos de testes utilizados


docConfigParam = [
                '_alpha'
                ,'_beta'
                ,'_gamma'
                ,'_delta'
                ,'_epsilon'
                ,'_zeta'
                ,'_eta'
                ,'_omicron'
                ,'_pi'
                ,'_rho'
                ,'_sigma'
                ,'_tau'
                ,'_upsilon'
                ,'_phi'
                ,'_chi'
    ]

def get_docconfig():
    """return all the different doc config"""
    return docConfigParam

mapping_translate = {
    'tensile':'Tração'
    ,'flexural':'Flexão'
    ,'compression':'Compressão'
    ,'shear':'Cisalhamento'
}

def print_docConfig()->str:
    '''
    Função para mostrar cada uma das pré-formatações configuradas para as máquinas.
    '''
    docConfigsClass = [
        _alpha
        ,_beta
        ,_gamma
        ,_delta
        ,_epsilon
        ,_zeta
        ,_eta
        ,_omicron
        ,_pi
        ,_rho
        ,_sigma
        ,_tau
        ,_upsilon
        ,_phi
        ,_chi
    ]
    returned_string = ""

    for each_docConfigClass, each_docConfigName in zip(docConfigsClass, docConfigParam):
        ClassInit = each_docConfigClass()

        string_tests = ""

        for each_test in ClassInit.testType:
            string_tests+=f'''
    - {mapping_translate[each_test]}
'''

        string_coluns = ""
        for each_colum in ClassInit.colunas:
            string_coluns+=f'''
    - {each_colum}
'''
        returned_string += f'''
_________________________________________________________________________________________

================================|  Configuração |========================================
docConfig {each_docConfigName}

Geralmente utilizado para testes de :

{string_tests}
================================|    Colunas    |========================================
{string_coluns}
_________________________________________________________________________________________
'''
    print(returned_string)
    return returned_string

def docConfigTranslator()->dict:
    '''
    Função para retornar um dicionario para as primeiras linhas de cada docConfig
    '''
    return {
     r"Time,Deslocamento,Força,Tensão à tração,Deformação à tração (Deslocamento),Strain Gauge 1/Axial Strain Ɛyy,Strain Gauge 1/Transverse Strain Ɛxx,Strain Gauge 1/Shear Strain Ɛxy,Strain Gauge 1/Minimum Normal Strain,Strain Gauge 1/Maximum Normal Strain,Strain Gauge 1/Poisson's Ratio -Ɛxx/Ɛyy,Strain Gauge 1/Axial Displacement dy,Strain Gauge 1/Transverse Displacement dx": '_alpha',
     r"Time,Deslocamento,Força,Tensão ao cisalhamento,Deformação ao cisalhamento (Deslocamento),Extensometer 1/Engineering Strain,Extensometer 1/True Strain,Extensometer 1/Distance Change L(t)-L0,Extensometer 1/Distance L(t),Extensometer 2/Engineering Strain,Extensometer 2/True Strain,Extensometer 2/Distance Change L(t)-L0,Extensometer 2/Distance L(t)" : "_omicron",
     r"Tempo;Deslocamento;Força;Deformação à compressão (Deslocamento);Tensão à compressão": '_pi',
     r"Time,Deslocamento,Força,Tensão à tração,Deformação à tração (Deslocamento),Strain Gauge 1/Axial Strain Ɛyy,Strain Gauge 1/Transverse Strain Ɛxx,Strain Gauge 1/Shear Strain Ɛxy,Strain Gauge 1/Minimum Normal Strain,Strain Gauge 1/Maximum Normal Strain,Strain Gauge 1/Poisson's Ratio -Ɛxx/Ɛyy,Strain Gauge 1/Axial Displacement dy,Strain Gauge 1/Transverse Displacement dx,Extensometer 1/Engineering Strain,Extensometer 1/True Strain,Extensometer 1/Distance Change L(t)-L0,Extensometer 1/Distance L(t)" : "_sigma",
     r"Tempo;Deslocamento;Força;Tensão à tração;Extens Bi Axial - Connector 6;Extens Bi Trans - Conector 5;Deformação à tração (Extens Bi Axial - Connector 6)": '_rho',
     r"Time,Deslocamento,Força,Tensão ao cisalhamento,Deformação ao cisalhamento (Deslocamento),Strain Gauge 1/Axial Strain Ɛyy,Strain Gauge 1/Transverse Strain Ɛxx,Strain Gauge 1/Shear Strain Ɛxy,Strain Gauge 1/Minimum Normal Strain,Strain Gauge 1/Maximum Normal Strain,Strain Gauge 1/Poisson's Ratio -Ɛxx/Ɛyy,Strain Gauge 1/Axial Displacement dy,Strain Gauge 1/Transverse Displacement dx": '_eta',
     r"Dados brutos;Resultados 2 da tabela Resultados": '_beta',
     r"Tempo;Deslocamento;Deslocamento à compressão;Força;Deformação à compressão (Deslocamento);Tensão à compressão": '_tau',
     r"Time,Deslocamento,Força,Tensão à tração,Deformação à tração (Deslocamento),Strain Gauge 1/Axial Strain Ɛyy,Strain Gauge 1/Transverse Strain Ɛxx,Strain Gauge 1/Shear Strain Ɛxy,Strain Gauge 1/Minimum Normal Strain,Strain Gauge 1/Maximum Normal Strain,Strain Gauge 1/Poisson's Ratio -Ɛxx/Ɛyy,Strain Gauge 1/Axial Displacement dy,Strain Gauge 1/Transverse Displacement dx,Extensometer 1/Engineering Strain,Extensometer 1/True Strain,Extensometer 1/Distance Change L(t)-L0,Extensometer 1/Distance L(t),Extensometer 2/Engineering Strain,Extensometer 2/True Strain,Extensometer 2/Distance Change L(t)-L0,Extensometer 2/Distance L(t)": '_upsilon',
     r"Tempo;Deslocamento;Deslocamento;Força;Deformação à compressão (Deslocamento);Tensão à compressão": '_phi',
     r"Test time,Temperature,Flexure angle,Deformation,Standard force": '_chi',
    }
