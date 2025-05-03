# %%
'''
Teste para gerar um gráfico de linha simples
'''
import os
import sys
import numpy as np
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))
from experimentalTreatingIsiPol.main import plot_helper
import matplotlib.pyplot as plt


fig, ax = plt.subplots(figsize=(6, 5))
n_samples = 100
ax = plot_helper(ax, x=np.linspace(1,n_samples, n_samples),
            y=np.random.normal(5,0.01, n_samples),
            xlabel='Amostra', ylabel='Espessura [mm]',
            label=r"Espessuras dos CP's, $\mu=5 [mm]$ e $\sigma=0.01 [mm]$")

# %%
'''
Teste para o gráfico de linha simples sem GRID
'''
import os
import sys
import numpy as np
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

fig, ax = plt.subplots(figsize=(6, 5))
n_samples = 100
ax = plot_helper(ax, x=np.linspace(1,n_samples, n_samples),
            y=np.random.normal(5,0.01, n_samples),
            xlabel='Amostra', ylabel='Espessura [mm]',
            label=r"Espessuras dos CP's, $\mu=5 [mm]$ e $\sigma=0.01 [mm]$")

ax.grid()

# %%
'''
Teste de geração de um gráfico de dispersão
'''
import os
import sys
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

from experimentalTreatingIsiPol.main import scatter_helper
import numpy as np
import matplotlib.pyplot as plt


fig, ax = plt.subplots(figsize=(6, 5))
n_samples = 100
ax = scatter_helper(ax, x=np.linspace(1,n_samples, n_samples),
            y=np.random.normal(5,0.01, n_samples),
            xlabel='Amostra', ylabel='Espessura [mm]',
            label=r"Espessuras dos CP's, $\mu=5 [mm]$ e $\sigma=0.01 [mm]$")
# %%
'''
Vários gráficos no mesmo meixo eixo (Método 1, sem utilizar o método automático)
'''
import os
import sys
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

from experimentalTreatingIsiPol.main import plot_helper, blue_tonalities_options
import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6, 5))
x = np.linspace(-10,10)
y1 = np.multiply(x,2)
y2 = np.power(x,1/2)
ax = scatter_helper(ax, x=x,
            y=y1,
            xlabel='x', ylabel='y',
            label=r"$2x$", color=blue_tonalities_options[0])

ax = scatter_helper(ax, x=x,
            y=y2,
            xlabel='x', ylabel='y',
            label=r"$x^{\frac{1}{2}}$", color = blue_tonalities_options[5], )

# %%
'''
Teste para o cálculo da propagação de erros por simulação de Monte Carlo
'''
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

from experimentalTreatingIsiPol.main import MonteCarloErrorPropagation
import numpy as np


def density(m,r,t):
    return m/(np.pi*r**2*t)

measured_r = [10.01,10.02,10.00,10.00]
measured_t = [1.01,1.02,1.00,1.05]
measured_m = [15.50,5.35,1.44,15.42,1.44]

ClassInit = MonteCarloErrorPropagation(density, measured_m, measured_r, measured_t)
ClassInit.ax.set_title('Densidade calculada: ' + f'{ClassInit.f_mean:.2f}+/- {2*ClassInit.f_MC.std():.2f}')
# %%
'''
Testes para a plotagem de múltiplos gráficos padronizados, no mesmo eixo, (Método 2)
'''
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))
import numpy as np
from experimentalTreatingIsiPol.main import several_plots_helper,several_scatter_helper
import matplotlib.pyplot as plt

def createFakeExperimentalData(y_data, n):
    new_y = []
    for i in range(n):
        r = np.random.rand()
        mean = 0.01*(r-1)+0.01*(r)

        Y_with_noise = y_data -y_data*(np.random.normal(mean,0.1,1))

        new_y.append(Y_with_noise)

    return new_y

number_of_especimes = 18
number_of_points = 1000
several_x = [np.linspace(0,number_of_points,number_of_points) for _ in range(number_of_especimes)] # criando 10 amostras para o eixo x

data_y = np.sqrt(np.linspace(0,number_of_points,number_of_points))
several_y = createFakeExperimentalData(data_y,number_of_especimes) # criando 10 amostras para o eixo y
several_labels = [f'data {i}' for i in range(number_of_especimes)]

fig, ax = plt.subplots(figsize=(8,3))

fig.get_figwidth()
ax = several_scatter_helper(ax,xs=several_x,ys=several_y,labels=several_labels,
                          xlabel=f'X data',ylabel='Y data',markersize=5)

# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

arq_path = r"C:\Users\user\Sistema Fiergs\DTI-Projeto SIQ4TFP - General\07_DOCUMENTOS_TECNICOS\DADOS_ENSAIOS\Senai\Placa 6\Tração 0_2024_10_22_com_tab\CP1.csv"
from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear

c = SeveralMechanicalTestingFittingLinear(
                            '_alpha', archive_name=arq_path,
                            direction = '11',
                            calculus_method='standard-ASTM-D3039',
                            x_max=0.1,
                            x_min=0.00,
                            verbose=False,
                            testType='tensile',
                            offset=0.2)
# %%
from experimentalTreatingIsiPol.docConfig import print_docConfig
print_docConfig()
# %%
# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

arq_path = r"C:\Users\user\Sistema Fiergs\DTI-Projeto SIQ4TFP - General\07_DOCUMENTOS_TECNICOS\DADOS_ENSAIOS\Senai\Placa 1\Flexão\Flexure_SENAI_Plate 01_1.csv"
from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear

c = SeveralMechanicalTestingFittingLinear(
                            '_beta', archive_name=arq_path,
                            direction = '11',
                            linearRegionSearchMethod='Custom',
                            x_min=0.4,
                            x_max=1,
                            verbose=False,
                            testType='flexural',
                            dimension_flexural={
                                'path' : r'C:\Users\user\Sistema Fiergs\DTI-Projeto SIQ4TFP - General\07_DOCUMENTOS_TECNICOS\medidas_CPS_flexao.xlsx'
                                ,'sheet_name' : 'Placa 1'
                            }
                            )
# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

arq_path = r"C:\Users\user\Sistema Fiergs\DTI-Projeto SIQ4TFP - General\07_DOCUMENTOS_TECNICOS\DADOS_ENSAIOS\Senai\Placa 1\Cisalhamento_2024_10_23\Specimen 5.csv"
from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear

c = SeveralMechanicalTestingFittingLinear(
                            '_eta', archive_name=arq_path,
                            direction = '11',
                            linearRegionSearchMethod='Custom',
                            x_min=0,
                            x_max=0.001,
                            calculus_method='standard-ASTM-D7078',
                            verbose=False,
                            testType='shear',
                            )
# %%
# %%
# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

arq_path = r"C:\Users\user\Sistema Fiergs\DTI-Projeto SIQ4TFP - General\07_DOCUMENTOS_TECNICOS\DADOS_ENSAIOS\Senai\Placa 11\Compressão 0\com tab\SENAI_Compression_Plate 11_01-11-24_1.csv"
from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear

c = SeveralMechanicalTestingFittingLinear(
                            '_pi', archive_name=arq_path,
                            direction = '11',
                            # linearRegionSearchMethod='Custom',
                            x_min=0.4,
                            x_max=1,
                            verbose=False,
                            testType='compression',
)
# %%
# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

arq_path = r"C:\Users\user\Sistema Fiergs\DTI-Projeto Ybyra - General\07_DOCUMENTOS_TECNICOS\ME03\Ensaios\Tração\Instron 68FM100\MP_Rota 2\Temp. BLENDA-CP Inj Tipo1\BPP20RE - 23C\Resultados DIC\SP1.csv"
from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear

c = SeveralMechanicalTestingFittingLinear(
                            '_alpha', archive_name=arq_path,
                            direction = '11',
                            # linearRegionSearchMethod='Custom',
                            x_min=0.4,
                            x_max=1,
                            verbose=False,
                            testType='tensile',
)

# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

arq_path = r"C:\Users\user\Sistema Fiergs\DTI-Projeto SIQ4TFP - General\07_DOCUMENTOS_TECNICOS\DADOS_ENSAIOS\Senai\Placa 1\Tração 0\Spécimen 460-1.csv"
from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear

c = SeveralMechanicalTestingFittingLinear(
                            '_alpha', archive_name=arq_path,
                            direction = '11',
                            calculus_method='standard-ASTM-D3039',
                            # linearRegionSearchMethod='Custom',
                            x_min=0.4,
                            x_max=1,
                            verbose=False,
                            testType='tensile',
)

# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

arq_path = r"C:\Users\user\Sistema Fiergs\DTI-Projeto SIQ4TFP - General\07_DOCUMENTOS_TECNICOS\DADOS_ENSAIOS\Senai\Placa 8\cisalhamento\PlotSet_2024-11-06_16-14-01.csv"
from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear

c = SeveralMechanicalTestingFittingLinear(
                            '_omicron', archive_name=arq_path,
                            direction = '11',
                            calculus_method='standard-ASTM-D7078',
                            # linearRegionSearchMethod='Custom',
                            x_min=0.4,
                            x_max=1,
                            verbose=False,
                            testType='shear',
)

# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

arq_path = r"C:\Users\user\Sistema Fiergs\DTI-Projeto SIQ4TFP - General\07_DOCUMENTOS_TECNICOS\DADOS_ENSAIOS\Senai\Placa 8\cisalhamento\PlotSet_2024-11-06_16-10-17.csv"
from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear

c = SeveralMechanicalTestingFittingLinear(
                            '_omicron', archive_name=arq_path,
                            direction = '11',
                            calculus_method='standard-ASTM-D7078',
                            # linearRegionSearchMethod='Custom',
                            x_min=0.4,
                            x_max=1,
                            verbose=False,
                            testType='shear',
)

# %%
# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

arq_path = r"C:\Users\user\Sistema Fiergs\DTI-Projeto SIQ4TFP - General\07_DOCUMENTOS_TECNICOS\DADOS_ENSAIOS\Senai\Placa 10\Tração 0_biaxial\SENAI_Biaxial Tensile 0_Plate 10_1.csv"
from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear

c = SeveralMechanicalTestingFittingLinear(
                            '_rho', archive_name=arq_path,
                            direction = '11',
                            calculus_method='standard-ASTM-D3039',
                            # linearRegionSearchMethod='Custom',
                            x_min=0.4,
                            x_max=1,
                            verbose=False,
                            testType='tensile',
)
# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

arq_path = r"C:\Users\user\Sistema Fiergs\DTI-Projeto SIQ4TFP - General\07_DOCUMENTOS_TECNICOS\DADOS_ENSAIOS\Senai\Placa 11\Compressão 0\com tab\SENAI_Compression_Plate 11_01-11-24_1.csv"
from experimentalTreatingIsiPol.main import MechanicalTestFittingLinear

c = MechanicalTestFittingLinear(
                            '_pi', archive_name=arq_path,
                            direction = '11',
                            # linearRegionSearchMethod='Custom',
                            x_min=0.4,
                            x_max=1,
                            verbose=False,
)

# %%

# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

arq_path = r"C:\Users\user\Sistema Fiergs\DTI-Projeto SIQ4TFP - General\07_DOCUMENTOS_TECNICOS\DADOS_ENSAIOS\ANALISE_E_TRATAMENTO\DADOS_ORGANIZADOS\EnsaiosL2\PLACA_10_L2_CP1.csv"
from experimentalTreatingIsiPol.docConfig import print_docConfig


print_docConfig()
# %%

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

arq_path = r"C:\Users\user\Sistema Fiergs\DTI-Projeto FlexCOP - General\07_DOCUMENTOS_TECNICOS\DADOS_CARACTERIZAÇÃO_CP\DADOS_COMPRESSAO\SYENSQO\90\Sy(2)-06-C-90-70.csv"

from experimentalTreatingIsiPol.main import MechanicalTestFittingLinear

c = MechanicalTestFittingLinear(
                            '_pi', archive_name=arq_path,
                            direction = '11',
                            # linearRegionSearchMethod='Custom',
                            # x_min=0.4,
                            # x_max=1,
                            verbose=True,
)

# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

arq_path = r"C:\Users\user\Sistema Fiergs\DTI-Projeto SIQ4TFP - General\07_DOCUMENTOS_TECNICOS\DADOS_ENSAIOS\Senai\Placa 10\Tração 0_biaxial\SENAI_Biaxial Tensile 0_Plate 10_1.csv"
from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear

c = SeveralMechanicalTestingFittingLinear(
                            '_rho', archive_name=arq_path,
                            direction = '11',
                            calculus_method='standard-ASTM-D3039',
                            verbose=False,
                            testType='tensile',
                            hide_plots = True
                            )
# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

arq_path = r"D:\Jonas\__TEST_LIB\experimental_data\CP02.csv"
from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear
from experimentalTreatingIsiPol.standards import get_standards

get_standards()

c = SeveralMechanicalTestingFittingLinear(
                            '_alpha', archive_name=arq_path,
                            direction = '11',
                            linearRegionSearchMethod='Custom',
                            calculus_method='standard-ASTM-D638',
                            # calculus_method='linearSearch',
                            verbose=False,
                            # testType='tensile',
                            x_min=0.008,
                            x_max=0.009
                            )

# %%
# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

arq_path = r"c:\Users\user\Sistema Fiergs\DTI-Projeto FlexCOP - General\07_DOCUMENTOS_TECNICOS\DADOS_CARACTERIZAÇÃO_CP\ANALISE_ESTATISTICA\..\ENSAIOS_2024\DADOS_CISALHAMENTO\SYENSQO\0\SEM_TAB\Sy(3)-02-S-0-02.csv"
from experimentalTreatingIsiPol.main import MechanicalTestFittingLinear, SeveralMechanicalTestingFittingLinear

from experimentalTreatingIsiPol.docConfig import print_docConfig
c = SeveralMechanicalTestingFittingLinear(docConfig='_omicron', archive_name=arq_path,
                                          testType='shear', direction='11',
                                calculus_method='standard-ASTM-D7078')

# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

arq_path = r"c:\Users\user\Sistema Fiergs\DTI-Projeto FlexCOP - General\07_DOCUMENTOS_TECNICOS\DADOS_CARACTERIZAÇÃO_CP\ANALISE_ESTATISTICA\..\ENSAIOS_2024\DADOS_CISALHAMENTO\SYENSQO\0\SEM_TAB\Sy(3)-02-S-0-02.csv"
from experimentalTreatingIsiPol.main import MechanicalTestFittingLinear, SeveralMechanicalTestingFittingLinear

from experimentalTreatingIsiPol.docConfig import print_docConfig
c = SeveralMechanicalTestingFittingLinear(docConfig='_eta', archive_name=arq_path,
                                          testType='shear', direction='11',
                                          autoDetectDocConfig=True,
                                calculus_method='standard-ASTM-D7078')

# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

arq_path = r"c:\Users\user\Sistema Fiergs\DTI-Projeto FlexCOP - General\07_DOCUMENTOS_TECNICOS\DADOS_CARACTERIZAÇÃO_CP\ANALISE_ESTATISTICA\..\ENSAIOS_2024\DADOS_TRACAO\SYENSQO\90\SEM_TAB\Sy(2)-07-T-90-06.csv"
from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear
from experimentalTreatingIsiPol.standards import get_standards

get_standards()

c = SeveralMechanicalTestingFittingLinear(
                            '_alpha', archive_name=arq_path,
                            direction = '11',
                            calculus_method='standard-ASTM-D3039',
                            verbose=False,
                            testType='tensile',
                            autoDetectDocConfig=True,
                            cutUnsedFinalPoints=True
                            )

# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear, MechanicalTestFittingLinear


path = r"c:\Users\user\Sistema Fiergs\DTI-Projeto FlexCOP - General\07_DOCUMENTOS_TECNICOS\DADOS_CARACTERIZAÇÃO_CP\ANALISE_ESTATISTICA\..\ENSAIOS_MECANICOS\ENSAIOS_2025\KIT_A\T_AMB\DADOS_CISALHAMENTO\TORAY\0\SEM_TAB\To(3)-06-S-0-01.csv"
c = SeveralMechanicalTestingFittingLinear(docConfig='_omicron', archive_name=path, testType='shear', filter_monoatomic_grow=False, calculus_method='standard-ASTM-D7078', filterInitPoints=False, cutUnsedFinalPoints=True)

# MechanicalTestFittingLinear(docConfig='_omicron', archive_name=path, autoDetectDocConfig='True', filter_monoatomic_grow=False)

# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear


path = r"D:\Jonas\PostProcessingData\DataArquives\standard-ASTM-D3039\test_1\Sy(1)-01-T-0-11.csv"
c = SeveralMechanicalTestingFittingLinear(docConfig='_alpha', archive_name=path, testType='tensile',
                                          filter_monoatomic_grow=True,
                                          calculus_method='standard-ASTM-D3039',
                                          filterInitPoints=True,
                                          cutUnsedFinalPoints=True,
                                          hide_plots = True)
c.dictMechanical['Tensão Máxima [MPa]']
# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear


path = r"D:\Jonas\PostProcessingData\DataArquives\standard-ASTM-D3039\test_2\PLACA_01_L_CP1.csv"

c = SeveralMechanicalTestingFittingLinear(docConfig='_alpha', archive_name=path, testType='tensile',
                                        #   filter_monoatomic_grow=True,
                                          calculus_method='standard-ASTM-D3039',
                                        #   filterInitPoints=True,
                                        #   cutUnsedFinalPoints=True,
                                        hide_plots = True
                                          )


with open('results.temp', 'w') as nf:

    print(c.dictMechanical['Tensão Máxima [MPa]'], file=nf)
    print([float(x) for x in c.dictMechanical['Poisson']], file=nf)
    print([float(x) for x in c.dictMechanical['Módulo de Young [MPa]']], file=nf)

# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear


path = r"D:\Jonas\PostProcessingData\DataArquives\standard-ASTM-D7264\test_1\PLACA_07_S_CP1.csv"

c = SeveralMechanicalTestingFittingLinear(docConfig='_eta', archive_name=path, testType='shear',
                                        #   filter_monoatomic_grow=True,
                                          calculus_method='standard-ASTM-D7078',
                                        #   filterInitPoints=True,
                                        #   cutUnsedFinalPoints=True,
                                        hide_plots = True
                                          )


with open('results.temp', 'w') as nf:

    print(c.dictMechanical['Tensão Máxima [MPa]'], file=nf)
    print([float(x) for x in c.dictMechanical['Poisson']], file=nf)
    print([float(x) for x in c.dictMechanical['Módulo de Cisalhamento [MPa]']], file=nf)

# %%
# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear


path = r"D:\Jonas\PostProcessingData\DataArquives\standard-ASTM-D7078\test_2\To(3)-05-S-0-59.csv"

c = SeveralMechanicalTestingFittingLinear(docConfig='_omicron', archive_name=path, testType='shear',
                                          filter_monoatomic_grow=False,
                                          calculus_method='standard-ASTM-D7078',
                                        #   filterInitPoints=True,
                                        #   cutUnsedFinalPoints=True,
                                        # hide_plots = True
                                          )
# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear


path = r"D:\Jonas\PostProcessingData\DataArquives\standard-ASTM-D3039\test_3\Tj(2)-07-T-90-01.csv"

c = SeveralMechanicalTestingFittingLinear(docConfig='_alpha', archive_name=path, testType='tensile',
                                          filter_monoatomic_grow=True,
                                          calculus_method='standard-ASTM-D3039',
                                        #   filterInitPoints=True,
                                        #   cutUnsedFinalPoints=True,
                                        # hide_plots = True
                                          )

# %%

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear


path = r"C:\Users\user\Sistema Fiergs\DTI-Projeto FlexCOP - General\07_DOCUMENTOS_TECNICOS\DADOS_CARACTERIZAÇÃO_CP\ENSAIOS_MECANICOS\ENSAIOS_2025\KIT_A\T_AMB\DADOS_COMPRESSAO\SYENSQO\90\COM_TAB\ADESIVO_460\Sy(2)-01-C-90-01.csv"

c = SeveralMechanicalTestingFittingLinear(docConfig='_tau', archive_name=path, testType='compression',
                                          filter_monoatomic_grow=True,
                                          # calculus_method='standard-ASTM-D3039',
                                        #   filterInitPoints=True,
                                          cutUnsedFinalPoints=True,
                                        # hide_plots = True
                                          )

# %%
c.dictMechanical['Tensão Máxima [MPa]']
# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

from experimentalTreatingIsiPol.main import MechanicalTestFittingLinear


path = r"C:\Users\user\Sistema Fiergs\DTI-Projeto FlexCOP - General\07_DOCUMENTOS_TECNICOS\DADOS_CARACTERIZAÇÃO_CP\ENSAIOS_MECANICOS\ENSAIOS_2025\KIT_A\T_AMB\DADOS_COMPRESSAO\SYENSQO\0\COM_TAB\ADESIVO_460\Sy(2)-07-C-0-01.csv"

c = MechanicalTestFittingLinear(docConfig='_tau', archive_name=path,
                                          # filter_monoatomic_grow=True,
                                          # calculus_method='standard-ASTM-D3039',
                                          # filterInitPoints=True,
                                          # cutUnsedFinalPoints=True,
                                          stress_min_cut = 180,
                                          stress_max_cut = 200,
                                          linearRegionSearchMethod='Custom',
                                        # hide_plots = True
                                          )

# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear

path = r"C:\Users\user\Sistema Fiergs\DTI-Projeto FlexCOP - General\07_DOCUMENTOS_TECNICOS\DADOS_CARACTERIZAÇÃO_CP\ENSAIOS_MECANICOS\ENSAIOS_2025\KIT_A\T_AMB\DADOS_COMPRESSAO\SYENSQO\0\COM_TAB\ADESIVO_460\Sy(2)-07-C-0-01.csv"


c = SeveralMechanicalTestingFittingLinear(docConfig='_tau', archive_name=path,
                                          # filter_monoatomic_grow=True,
                                          # calculus_method='standard-ASTM-D3039',
                                          testType='compression',
                                          filterInitPoints=True,
                                          # cutUnsedFinalPoints=True,
                                          filterCompressionCompensation = False,
                                          linearRegionSearchMethod='Custom',
                                          stress_min_cut = 180,
                                          stress_max_cut = 220,
                                          truncate_data = 0.005
                                        # hide_plots = True
                                          )

# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear, SmoothDataType

path = r"D:\Jonas\FlexCop\TesteTensile\Nova pasta\To(2)-18-T-90-22extensometro.csv"

s = SmoothDataType(
    window_length=15,
    jump_space=20,
    methodology='mean',
)

# Aplicar depois para selecionar a região de filtro inicial manualmente!!!!!
c = SeveralMechanicalTestingFittingLinear(docConfig='_upsilon', archive_name=path,
                                          # filter_monoatomic_grow=True,
                                          calculus_method='standard-ASTM-D3039',
                                          testType='tensile',
                                          filter_monoatomic_grow=False,
                                          filterInitPoints=True,
                                          smoth_data=s
                                          # cutUnsedFinalPoints=True,
                                          )

# %%
path = r"D:\Jonas\FlexCop\TesteTensile\To(2)-18-T-90-22.csv"



c = SeveralMechanicalTestingFittingLinear(docConfig='_alpha', archive_name=path,
                                          # filter_monoatomic_grow=True,
                                          calculus_method='standard-ASTM-D3039',
                                          testType='tensile',
                                          filterInitPoints=True,
                                          filter_monoatomic_grow=True,
                                          # cutUnsedFinalPoints=True,
                                          )

# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear
path = r"D:\Jonas\RandomWorks\OneDrive_1_18-03-2025\254_25\Cisalhamento\CP1.csv"
SeveralMechanicalTestingFittingLinear(docConfig='_eta', archive_name=path, testType='shear',
                                          filter_monoatomic_grow=False,
                                          calculus_method='standard-ASTM-D7078',
                                          filterInitPoints=False
                                          )

# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear
path = r"C:\Users\user\Sistema Fiergs\DTI-Projeto FlexCOP - General\07_DOCUMENTOS_TECNICOS\DADOS_CARACTERIZAÇÃO_CP\ENSAIOS_MECANICOS\ENSAIOS_2025\KIT_A\T_AMB\DADOS_CISALHAMENTO\TORAY\0\SEM_TAB\To(3)-06-S-0-01.csv"

s = SmoothDataType(
    window_length=10,
    jump_space=10,
    methodology='mean',
)

c = SeveralMechanicalTestingFittingLinear(docConfig='_omicron',
                                          archive_name=path, testType='shear',
                                          filter_monoatomic_grow=False,
                                          calculus_method='standard-ASTM-D7078',
                                          filterInitPoints=False,
                                          smoth_data=s
                                          )

# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear, SmoothDataType,filterGradiendY
path = r"C:\Users\user\Sistema Fiergs\DTI-Projeto FlexCOP - General\07_DOCUMENTOS_TECNICOS\DADOS_CARACTERIZAÇÃO_CP\ENSAIOS_MECANICOS\ENSAIOS_2025\KIT_A\T_AMB\DADOS_CISALHAMENTO\TORAY\0\SEM_TAB\To(3)-06-S-0-01.csv"

s = SmoothDataType(
    methodology='polynomial',
    num_divisions=1
)

g = filterGradiendY(
    gradient_limit=8
)

c = SeveralMechanicalTestingFittingLinear(docConfig='_omicron',
                                          archive_name=path, testType='shear',
                                          filter_monoatomic_grow=False,
                                          calculus_method='standard-ASTM-D7078',
                                          filterInitPoints=False,
                                          smoth_data=s,
                                          filterGradiendY=g
                                          )

# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

from experimentalTreatingIsiPol.main import MechanicalTestFittingLinear, SmoothDataType,filterGradiendY
path = r"D:\Jonas\FlexCop\TesteTensile\Nova pasta (2)\To(3)-06-S-0-07.csv"
c = MechanicalTestFittingLinear(docConfig='_eta',
                                        archive_name=path,
                                        filter_monoatomic_grow=False,
                                        filterInitPoints=False,
                                        smoth_data=None,
                                        verbose=False
                                        )

c.new_x

# %%
path=r"C:\Users\user\Sistema Fiergs\DTI-Projeto FlexCOP - General\07_DOCUMENTOS_TECNICOS\DADOS_CARACTERIZAÇÃO_CP\ENSAIOS_MECANICOS\ENSAIOS_2025\KIT_A\T_AMB\DADOS_COMPRESSAO\SYENSQO\90\COM_TAB\ADESIVO_460\Sy(2)-01-C-90-01.csv"


import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear, SmoothDataType,filterGradiendY

c = SeveralMechanicalTestingFittingLinear(docConfig='_phi',
                                          archive_name=path, testType='compression',
                                          filter_monoatomic_grow=False,
                                          calculus_method='standard-ASTM-D3039',
                                          filterInitPoints=False,
                                          )

# %%
# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

from experimentalTreatingIsiPol.main import MechanicalTestFittingLinear
path = r"C:\Users\user\Sistema Fiergs\DTI-Projeto FlexCOP - General\07_DOCUMENTOS_TECNICOS\DADOS_CARACTERIZAÇÃO_CP\20250328_Flexao\DADOS_ORGANIZADOS\SYENSQO\T_ALTA\Sy(2)-04-F-0-48.csv"
c = MechanicalTestFittingLinear(docConfig='_chi',
                                        archive_name=path,
                                        filter_monoatomic_grow=False,
                                        filterInitPoints=False,
                                        smoth_data=None,
                                        )

c.MeasureFlexuralModulus(
    length=44.5,
    thickness=2.218,
    width=13.48,
    calculus_method='standard-ASTM-D7264'
)
c.E


# %%
# %%
path=r"C:\Users\user\Sistema Fiergs\DTI-Projeto FlexCOP - General\07_DOCUMENTOS_TECNICOS\DADOS_CARACTERIZAÇÃO_CP\ENSAIOS_MECANICOS\ENSAIOS_2025\KIT_A\T_AMB\DADOS_COMPRESSAO\SYENSQO\90\COM_TAB\ADESIVO_460\Sy(2)-01-C-90-01.csv"


import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src'))

from experimentalTreatingIsiPol.main import SeveralMechanicalTestingFittingLinear, SmoothDataType,filterGradiendY


arq_path = r"D:\Jonas\PostProcessingData\DataArquives\standard-ASTM-D3039\test_1\Sy(1)-01-T-0-11.csv"
c = SeveralMechanicalTestingFittingLinear(docConfig='_alpha', archive_name=arq_path, testType='tensile',
                                                #   filter_monoatomic_grow=True,
                                                calculus_method='standard-ASTM-D3039',
                                                #   filterInitPoints=True,
                                                #   cutUnsedFinalPoints=True
                                                # save_results=os.getcwd()
                                                hide_plots = False
                                                )


c.dictMechanical
# %%
