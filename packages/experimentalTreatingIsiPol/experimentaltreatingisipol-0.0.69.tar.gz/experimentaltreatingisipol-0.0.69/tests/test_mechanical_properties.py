# %%
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), "..","src"))

from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear


# %%

def assertAlmostEqualList(list1 : list, list2 : list,tol=0.05)->bool:

    for l1, l2 in zip(list1, list2):
        diff = abs(l1/l2-1)
        if diff>tol:
            sys.stderr.write(f'''
========================================
                Elemento Errado:

{l1}!={l2} (tol {tol})

========================================
''')
            return False

    return True

def sort_dictValues(dictName, *keysName)->None:

    for each_col in keysName:
        dictName[each_col].sort()



class testStandard_ASTM_D3039(unittest.TestCase):
    '''
    Classe para testar as funcionalidades relacionadas à norma D3039
    '''
    max_stress_pvdfCarbon = [2758.66089, 2740.17212, 2701.99438, 2257.97363, 2807.00024, 2404.85962, 2662.55615]
    poisson_ratio_pvdfCarbon = [0.3263495564132124, 0.3619988961918619, 0.3718051518492534, 0.3810692989928346, 0.3763219888727382, 0.37431735056866566, 0.4106076571830002]
    young_modulus_pvdfCarbon = [129560.16367692061, 133266.79815225146, 137586.95573508294, 136462.3534900897, 131745.07492583198, 140357.15849779092, 139242.57266465313]

    max_stress_epoxyCarbon = [1534.57373, 1626.40161, 1680.35168, 1626.23706]
    poisson_ratio_epoxyCarbon  = [0.46531082502629884, 0.17522825323567767, 0.21420337793815464, 0.2944129310777572]
    young_modulus_epoxyCarbon  = [141274.91905092163, 113468.4504707437, 117910.20293629944, 126721.52181324299]

    def __init__(self, methodName = "runTest"):
        self.max_stress_pvdfCarbon.sort()
        self.poisson_ratio_pvdfCarbon.sort()
        self.young_modulus_pvdfCarbon.sort()

        self.max_stress_epoxyCarbon.sort()
        self.poisson_ratio_epoxyCarbon.sort()
        self.young_modulus_epoxyCarbon.sort()

        super().__init__(methodName)

    def test_pvdf_carbon(self):

        path = os.path.join(os.getcwd(),
                            "DataArquives",
                            "standard-ASTM-D3039",
                            "test_1",
                            "Sy(1)-01-T-0-11.csv")



        c = SeveralMechanicalTestingFittingLinear(docConfig='_alpha', archive_name=path, testType='tensile',
                                                #   filter_monoatomic_grow=True,
                                                calculus_method='standard-ASTM-D3039',
                                                #   filterInitPoints=True,
                                                #   cutUnsedFinalPoints=True
                                                hide_plots=True
                                                )

        sort_dictValues(c.dictMechanical, 'Tensão Máxima [MPa]','Poisson','Módulo de Young [MPa]')
        self.assertTrue(assertAlmostEqualList(self.max_stress_pvdfCarbon, c.dictMechanical['Tensão Máxima [MPa]'], tol=0.01), msg='Erro no cálculo da tensão máxima')
        self.assertTrue(assertAlmostEqualList(self.poisson_ratio_pvdfCarbon, c.dictMechanical['Poisson'], tol=0.01), msg='Erro no cálculo do Poisson')
        self.assertTrue(assertAlmostEqualList(self.young_modulus_pvdfCarbon, c.dictMechanical['Módulo de Young [MPa]'], tol=0.01), msg='Erro no cálculo do Módulo de Young')

    def test_pvdf_carbon_monoatomic_growth(self):

        path = os.path.join(os.getcwd(),
                            "DataArquives",
                            "standard-ASTM-D3039",
                            "test_1",
                            "Sy(1)-01-T-0-11.csv")



        c = SeveralMechanicalTestingFittingLinear(docConfig='_alpha', archive_name=path, testType='tensile',
                                                #   filter_monoatomic_grow=True,
                                                calculus_method='standard-ASTM-D3039',
                                                #   filterInitPoints=True,
                                                #   cutUnsedFinalPoints=True
                                                hide_plots=True
                                                )

        sort_dictValues(c.dictMechanical, 'Tensão Máxima [MPa]','Poisson','Módulo de Young [MPa]')
        self.assertTrue(assertAlmostEqualList(self.max_stress_pvdfCarbon, c.dictMechanical['Tensão Máxima [MPa]'], tol=0.01), msg='Erro no cálculo da tensão máxima')
        self.assertTrue(assertAlmostEqualList(self.poisson_ratio_pvdfCarbon, c.dictMechanical['Poisson'], tol=0.01), msg='Erro no cálculo do Poisson')
        self.assertTrue(assertAlmostEqualList(self.young_modulus_pvdfCarbon, c.dictMechanical['Módulo de Young [MPa]'], tol=0.01), msg='Erro no cálculo do Módulo de Young')


    def test_pvdf_carbon_cutFinalPoints(self):

        path = os.path.join(os.getcwd(),
                            "DataArquives",
                            "standard-ASTM-D3039",
                            "test_1",
                            "Sy(1)-01-T-0-11.csv")



        c = SeveralMechanicalTestingFittingLinear(docConfig='_alpha', archive_name=path, testType='tensile',
                                                #   filter_monoatomic_grow=True,
                                                calculus_method='standard-ASTM-D3039',
                                                #   filterInitPoints=True,
                                                  cutUnsedFinalPoints=True,
                                                hide_plots=True
                                                )

        sort_dictValues(c.dictMechanical, 'Tensão Máxima [MPa]','Poisson','Módulo de Young [MPa]')

        self.assertTrue(assertAlmostEqualList(self.max_stress_pvdfCarbon, c.dictMechanical['Tensão Máxima [MPa]'], tol=0.05), msg='Erro no cálculo da tensão máxima')
        self.assertTrue(assertAlmostEqualList(self.poisson_ratio_pvdfCarbon, c.dictMechanical['Poisson'], tol=0.05), msg='Erro no cálculo do Poisson')
        self.assertTrue(assertAlmostEqualList(self.young_modulus_pvdfCarbon, c.dictMechanical['Módulo de Young [MPa]'], tol=0.05), msg='Erro no cálculo do Módulo de Young')


    def test_pvdf_carbon_filter_init_points(self):

        path = os.path.join(os.getcwd(),
                            "DataArquives",
                            "standard-ASTM-D3039",
                            "test_1",
                            "Sy(1)-01-T-0-11.csv")



        c = SeveralMechanicalTestingFittingLinear(docConfig='_alpha', archive_name=path, testType='tensile',
                                                #   filter_monoatomic_grow=True,
                                                calculus_method='standard-ASTM-D3039',
                                                  filterInitPoints=True,
                                                #   cutUnsedFinalPoints=True
                                                hide_plots=True
                                                )

        sort_dictValues(c.dictMechanical, 'Tensão Máxima [MPa]','Poisson','Módulo de Young [MPa]')

        self.assertTrue(assertAlmostEqualList(self.max_stress_pvdfCarbon, c.dictMechanical['Tensão Máxima [MPa]'], tol=0.01), msg='Erro no cálculo da tensão máxima')
        self.assertTrue(assertAlmostEqualList(self.poisson_ratio_pvdfCarbon, c.dictMechanical['Poisson'], tol=0.01), msg='Erro no cálculo do Poisson')
        self.assertTrue(assertAlmostEqualList(self.young_modulus_pvdfCarbon, c.dictMechanical['Módulo de Young [MPa]'], tol=0.01), msg='Erro no cálculo do Módulo de Young')



    def test_epoxy_carbon(self):

        path = os.path.join(os.getcwd(),
                            "DataArquives",
                            "standard-ASTM-D3039",
                            "test_2",
                            "PLACA_01_L_CP1.csv")



        c = SeveralMechanicalTestingFittingLinear(docConfig='_alpha', archive_name=path, testType='tensile',
                                                #   filter_monoatomic_grow=True,
                                                calculus_method='standard-ASTM-D3039',
                                                #   filterInitPoints=True,
                                                #   cutUnsedFinalPoints=True
                                                hide_plots=True
                                                )
        sort_dictValues(c.dictMechanical, 'Tensão Máxima [MPa]','Poisson','Módulo de Young [MPa]')

        self.assertTrue(assertAlmostEqualList(self.max_stress_epoxyCarbon, c.dictMechanical['Tensão Máxima [MPa]'], tol=0.01), msg='Erro no cálculo da tensão máxima')
        self.assertTrue(assertAlmostEqualList(self.poisson_ratio_epoxyCarbon, c.dictMechanical['Poisson'], tol=0.01), msg='Erro no cálculo do Poisson')
        self.assertTrue(assertAlmostEqualList(self.young_modulus_epoxyCarbon, c.dictMechanical['Módulo de Young [MPa]'], tol=0.01), msg='Erro no cálculo do Módulo de Young')


    def test_epoxy_carbon_monoatomic_growth(self):

        path = os.path.join(os.getcwd(),
                            "DataArquives",
                            "standard-ASTM-D3039",
                            "test_2",
                            "PLACA_01_L_CP1.csv")



        c = SeveralMechanicalTestingFittingLinear(docConfig='_alpha', archive_name=path, testType='tensile',
                                                  filter_monoatomic_grow=True,
                                                calculus_method='standard-ASTM-D3039',
                                                #   filterInitPoints=True,
                                                #   cutUnsedFinalPoints=True
                                                hide_plots=True
                                                )

        sort_dictValues(c.dictMechanical, 'Tensão Máxima [MPa]','Poisson','Módulo de Young [MPa]')

        self.assertTrue(assertAlmostEqualList(self.max_stress_epoxyCarbon, c.dictMechanical['Tensão Máxima [MPa]'], tol=0.01), msg='Erro no cálculo da tensão máxima')
        self.assertTrue(assertAlmostEqualList(self.poisson_ratio_epoxyCarbon, c.dictMechanical['Poisson'], tol=0.01), msg='Erro no cálculo do Poisson')
        self.assertTrue(assertAlmostEqualList(self.young_modulus_epoxyCarbon, c.dictMechanical['Módulo de Young [MPa]'], tol=0.01), msg='Erro no cálculo do Módulo de Young')

    def test_epoxy_carbon_filter_init_points(self):

        path = os.path.join(os.getcwd(),
                            "DataArquives",
                            "standard-ASTM-D3039",
                            "test_2",
                            "PLACA_01_L_CP1.csv")



        c = SeveralMechanicalTestingFittingLinear(docConfig='_alpha', archive_name=path, testType='tensile',
                                                #   filter_monoatomic_grow=True,
                                                calculus_method='standard-ASTM-D3039',
                                                  filterInitPoints=True,
                                                #   cutUnsedFinalPoints=True
                                                hide_plots=True
                                                )

        sort_dictValues(c.dictMechanical, 'Tensão Máxima [MPa]','Poisson','Módulo de Young [MPa]')

        self.assertTrue(assertAlmostEqualList(self.max_stress_epoxyCarbon, c.dictMechanical['Tensão Máxima [MPa]'], tol=0.01), msg='Erro no cálculo da tensão máxima')
        self.assertTrue(assertAlmostEqualList(self.poisson_ratio_epoxyCarbon, c.dictMechanical['Poisson'], tol=0.01), msg='Erro no cálculo do Poisson')
        self.assertTrue(assertAlmostEqualList(self.young_modulus_epoxyCarbon, c.dictMechanical['Módulo de Young [MPa]'], tol=0.01), msg='Erro no cálculo do Módulo de Young')

    def test_epoxy_carbon_cutfinalpoints(self):

        path = os.path.join(os.getcwd(),
                            "DataArquives",
                            "standard-ASTM-D3039",
                            "test_2",
                            "PLACA_01_L_CP1.csv")

        c = SeveralMechanicalTestingFittingLinear(docConfig='_alpha', archive_name=path, testType='tensile',
                                                #   filter_monoatomic_grow=True,
                                                calculus_method='standard-ASTM-D3039',
                                                #   filterInitPoints=True,
                                                  cutUnsedFinalPoints=True,
                                                hide_plots=True
                                                )
        sort_dictValues(c.dictMechanical, 'Tensão Máxima [MPa]','Poisson','Módulo de Young [MPa]')

        self.assertTrue(assertAlmostEqualList(self.max_stress_epoxyCarbon, c.dictMechanical['Tensão Máxima [MPa]']), msg='Erro no cálculo da tensão máxima')
        self.assertTrue(assertAlmostEqualList(self.poisson_ratio_epoxyCarbon, c.dictMechanical['Poisson']), msg='Erro no cálculo do Poisson')
        self.assertTrue(assertAlmostEqualList(self.young_modulus_epoxyCarbon, c.dictMechanical['Módulo de Young [MPa]']), msg='Erro no cálculo do Módulo de Young')

class TestStandard_D7264(unittest.TestCase):

    max_stress_epoxy_carbon = [57.52484, 59.60385, 56.31638, 61.19859, 59.83554]
    shear_modulus_epoxy_carbon = [2887.8570425532507, 2890.9332152042984, 2563.8302030886425, 2926.261845072545, 2927.3145248330734]


    max_stress_peek_carbon = [84.96261, 84.16097, 82.6439, 84.21804]
    shear_modulus_peek_carbon = [5366.801931653137, 5429.230843756828, 6051.609287496136, 5427.641496944463]

    def __init__(self, methodName = "runTest"):

        self.max_stress_epoxy_carbon.sort()
        self.shear_modulus_epoxy_carbon.sort()

        self.max_stress_peek_carbon.sort()
        self.shear_modulus_peek_carbon.sort()

        super().__init__(methodName)

    def test_epoxy_carbon(self):

        path = os.path.join(os.getcwd(),
                            "DataArquives",
                            "standard-ASTM-D7078",
                            "test_1",
                            "PLACA_07_S_CP1.csv")

        c = SeveralMechanicalTestingFittingLinear(docConfig='_eta', archive_name=path, testType='shear',
                                                  filter_monoatomic_grow=False,
                                                calculus_method='standard-ASTM-D7078',
                                                #   filterInitPoints=True,
                                                #   cutUnsedFinalPoints=True,
                                                hide_plots = True
        )

        sort_dictValues(c.dictMechanical, 'Tensão Máxima [MPa]','Módulo de Cisalhamento [MPa]')


        self.assertTrue(assertAlmostEqualList(self.max_stress_epoxy_carbon, c.dictMechanical['Tensão Máxima [MPa]'], tol=0.01), msg='Erro no cálculo da tensão máxima')
        self.assertTrue(assertAlmostEqualList(self.shear_modulus_epoxy_carbon, c.dictMechanical['Módulo de Cisalhamento [MPa]'], tol=0.01), msg='Erro no cálculo do Módulo de Cisalhamento')

    def test_epoxy_carbon_filter_monotomic_growth(self):

        path = os.path.join(os.getcwd(),
                            "DataArquives",
                            "standard-ASTM-D7078",
                            "test_1",
                            "PLACA_07_S_CP1.csv")

        c = SeveralMechanicalTestingFittingLinear(docConfig='_eta', archive_name=path, testType='shear',
                                                  filter_monoatomic_grow=True,
                                                calculus_method='standard-ASTM-D7078',
                                                #   filterInitPoints=True,
                                                #   cutUnsedFinalPoints=True,
                                                hide_plots = True
        )

        sort_dictValues(c.dictMechanical, 'Tensão Máxima [MPa]','Módulo de Cisalhamento [MPa]')

        self.assertTrue(assertAlmostEqualList(self.max_stress_epoxy_carbon, c.dictMechanical['Tensão Máxima [MPa]'], tol=0.01), msg='Erro no cálculo da tensão máxima')
        self.assertTrue(assertAlmostEqualList(self.shear_modulus_epoxy_carbon, c.dictMechanical['Módulo de Cisalhamento [MPa]'], tol=0.01), msg='Erro no cálculo do Módulo de Cisalhamento')



    def test_epoxy_carbon_filter_initPoints(self):

        path = os.path.join(os.getcwd(),
                            "DataArquives",
                            "standard-ASTM-D7078",
                            "test_1",
                            "PLACA_07_S_CP1.csv")

        c = SeveralMechanicalTestingFittingLinear(docConfig='_eta', archive_name=path, testType='shear',
                                                  filter_monoatomic_grow=False,
                                                calculus_method='standard-ASTM-D7078',
                                                  filterInitPoints=True,
                                                #   cutUnsedFinalPoints=True,
                                                hide_plots = True
        )

        sort_dictValues(c.dictMechanical, 'Tensão Máxima [MPa]','Módulo de Cisalhamento [MPa]')


        self.assertTrue(assertAlmostEqualList(self.max_stress_epoxy_carbon, c.dictMechanical['Tensão Máxima [MPa]'], tol=0.01), msg='Erro no cálculo da tensão máxima')
        self.assertTrue(assertAlmostEqualList(self.shear_modulus_epoxy_carbon, c.dictMechanical['Módulo de Cisalhamento [MPa]'], tol=0.01), msg='Erro no cálculo do Módulo de Cisalhamento')


    @unittest.skip('Ainda há diferenças ao se eliminar os pontos finais')
    def test_epoxy_carbon_cutUnsedFinalPoints(self):

        path = os.path.join(os.getcwd(),
                            "DataArquives",
                            "standard-ASTM-D7078",
                            "test_1",
                            "PLACA_07_S_CP1.csv")

        c = SeveralMechanicalTestingFittingLinear(docConfig='_eta', archive_name=path, testType='shear',
                                                  filter_monoatomic_grow=False,
                                                calculus_method='standard-ASTM-D7078',
                                                #   filterInitPoints=True,
                                                  cutUnsedFinalPoints=True,
                                                hide_plots = True
        )

        sort_dictValues(c.dictMechanical, 'Tensão Máxima [MPa]','Módulo de Cisalhamento [MPa]')


        self.assertTrue(assertAlmostEqualList(self.max_stress_epoxy_carbon, c.dictMechanical['Tensão Máxima [MPa]']), msg='Erro no cálculo da tensão máxima')
        self.assertTrue(assertAlmostEqualList(self.shear_modulus_epoxy_carbon, c.dictMechanical['Módulo de Cisalhamento [MPa]']), msg='Erro no cálculo do Módulo de Cisalhamento')


    def test_peek_carbon(self):

        path = os.path.join(os.getcwd(),
                            "DataArquives",
                            "standard-ASTM-D7078",
                            "test_2",
                            "To(3)-05-S-0-59.csv")

        c = SeveralMechanicalTestingFittingLinear(docConfig='_omicron', archive_name=path, testType='shear',
                                                  filter_monoatomic_grow=False,
                                                calculus_method='standard-ASTM-D7078',
                                                #   filterInitPoints=True,
                                                #   cutUnsedFinalPoints=True,
                                                hide_plots = True
        )

        sort_dictValues(c.dictMechanical, 'Tensão Máxima [MPa]','Módulo de Cisalhamento [MPa]')

        self.assertTrue(assertAlmostEqualList(self.max_stress_peek_carbon, c.dictMechanical['Tensão Máxima [MPa]'], tol=0.01), msg='Erro no cálculo da tensão máxima')
        self.assertTrue(assertAlmostEqualList(self.shear_modulus_peek_carbon, c.dictMechanical['Módulo de Cisalhamento [MPa]'], tol=0.01), msg='Erro no cálculo do Módulo de Cisalhamento')

    @unittest.skip('Não é bem um erro. O corpo de prova não tem dados monoatomicamente crescentes')
    def test_peek_carbon_monoatomic_growth(self):

        path = os.path.join(os.getcwd(),
                            "DataArquives",
                            "standard-ASTM-D7078",
                            "test_2",
                            "To(3)-05-S-0-59.csv")

        c = SeveralMechanicalTestingFittingLinear(docConfig='_omicron', archive_name=path, testType='shear',
                                                  filter_monoatomic_grow=True,
                                                calculus_method='standard-ASTM-D7078',
                                                #   filterInitPoints=True,
                                                #   cutUnsedFinalPoints=True,
                                                hide_plots = True
        )

        sort_dictValues(c.dictMechanical, 'Tensão Máxima [MPa]','Módulo de Cisalhamento [MPa]')

        self.assertTrue(assertAlmostEqualList(self.max_stress_peek_carbon, c.dictMechanical['Tensão Máxima [MPa]']), msg='Erro no cálculo da tensão máxima')
        self.assertTrue(assertAlmostEqualList(self.shear_modulus_peek_carbon, c.dictMechanical['Módulo de Cisalhamento [MPa]']), msg='Erro no cálculo do Módulo de Cisalhamento')

    def test_peek_carbon_cut_init_points(self):

      path = os.path.join(os.getcwd(),
                          "DataArquives",
                          "standard-ASTM-D7078",
                          "test_2",
                          "To(3)-05-S-0-59.csv")

      c = SeveralMechanicalTestingFittingLinear(docConfig='_omicron', archive_name=path, testType='shear',
                                                filter_monoatomic_grow=False,
                                              calculus_method='standard-ASTM-D7078',
                                              filterInitPoints=True,
                                              #   cutUnsedFinalPoints=True,
                                              hide_plots = True
      )

      sort_dictValues(c.dictMechanical, 'Tensão Máxima [MPa]','Módulo de Cisalhamento [MPa]')


      self.assertTrue(assertAlmostEqualList(self.max_stress_peek_carbon, c.dictMechanical['Tensão Máxima [MPa]']), msg='Erro no cálculo da tensão máxima')
      self.assertTrue(assertAlmostEqualList(self.shear_modulus_peek_carbon, c.dictMechanical['Módulo de Cisalhamento [MPa]']), msg='Erro no cálculo do Módulo de Cisalhamento')

    @unittest.skip('Erro encontrado. Correcao a ser implementada')
    def test_peek_carbon_cut_final_points(self):

      path = os.path.join(os.getcwd(),
                          "DataArquives",
                          "standard-ASTM-D7078",
                          "test_2",
                          "To(3)-05-S-0-59.csv")

      c = SeveralMechanicalTestingFittingLinear(docConfig='_omicron', archive_name=path, testType='shear',
                                                filter_monoatomic_grow=False,
                                              calculus_method='standard-ASTM-D7078',
                                              # filterInitPoints=True,
                                                cutUnsedFinalPoints=True,
                                              hide_plots = True
      )

      sort_dictValues(c.dictMechanical, 'Tensão Máxima [MPa]','Módulo de Cisalhamento [MPa]')


      self.assertTrue(assertAlmostEqualList(self.max_stress_peek_carbon, c.dictMechanical['Tensão Máxima [MPa]']), msg='Erro no cálculo da tensão máxima')
      self.assertTrue(assertAlmostEqualList(self.shear_modulus_peek_carbon, c.dictMechanical['Módulo de Cisalhamento [MPa]']), msg='Erro no cálculo do Módulo de Cisalhamento')

class TestCompression(unittest.TestCase):

    COMPRESSION_RESULTS = [96.225, 80.9585, 83.3299, 83.0292, 89.5599]

    def __init__(self, methodName = "runTest"):
        '''
        ordenando os dados
        '''
        self.COMPRESSION_RESULTS.sort()
        super().__init__(methodName)


    def test_simple_compression(self):

        path = os.path.join(os.getcwd(),
                            "DataArquives",
                            "Compression",
                            "test_1",
                            "Sy(2)-01-C-90-01.csv")

        c = SeveralMechanicalTestingFittingLinear(docConfig='_tau', archive_name=path, testType='compression',
                                                #   filterInitPoints=True,
                                                #   cutUnsedFinalPoints=True,
                                                hide_plots = True
        )

        sort_dictValues(c.dictMechanical, 'Tensão Máxima [MPa]')


        self.assertTrue(assertAlmostEqualList(self.COMPRESSION_RESULTS, c.dictMechanical['Tensão Máxima [MPa]'], tol=0.01), msg='Erro no cálculo da tensão máxima')
