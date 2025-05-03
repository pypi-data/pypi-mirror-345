# %%
'''
Deselvolvimento de uma metodologia para leitura e tratamento de dados de curva de ângulo de contato
'''
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class ContactAngleArqConfig():
    '''
    Classe usada para tipar o tipo de dado proveniente das colunas do excel do ângulo de contato
    '''
    def __init__(self):

        self.TIME = 'Time [s]'
        self.CALEFT = 'CA left [°]'
        self.CARIGHT = 'CA right [°]'
        self.CA_MEAN = 'CA mean [°]'
        self.VOLUME = 'Volume [μl]'
        self.BASELINE = 'Baseline [mm]'
        self.TEMPERATURA = 'Temperature [°C]'


class Analyser():

    def __init__(self,
                 arq_path
                 ):
        """
        arq_path : caminho do arquivo
        """
        self.data = pd.read_excel(arq_path)
        self.arq_columns = ContactAngleArqConfig()
        self.smoothed_data = {}

    def mean_filter(self, **kwargs):
        '''
        Aplicação de filtro dia media movel
        '''

        if kwargs.get('window_size'):
            window_size = kwargs.get('window_size')
        else:
            window_size = 50
        self.smoothed_data[self.arq_columns.CA_MEAN] = self.data[self.arq_columns.CA_MEAN].rolling(window=window_size, center=True, min_periods=1).mean().fillna('ffill')
        self.smoothed_data[self.arq_columns.CALEFT] = self.data[self.arq_columns.CALEFT].rolling(window=window_size, center=True).mean()
        self.smoothed_data[self.arq_columns.CARIGHT] = self.data[self.arq_columns.CARIGHT].rolling(window=window_size, center=True).mean()
        self.smoothed_data[self.arq_columns.TIME] = self.data[self.arq_columns.TIME]

    def median_filter(self, **kwargs):
        '''
        Aplicação de filtro dia media movel
        '''

        if kwargs.get('window_size'):
            window_size = kwargs.get('window_size')
        else:
            window_size = 50


        self.smoothed_data[self.arq_columns.CA_MEAN] = self.data[self.arq_columns.CA_MEAN].rolling(window=window_size, center=True,min_periods=1).median().fillna(method='ffill')
        self.smoothed_data[self.arq_columns.CALEFT] = self.data[self.arq_columns.CALEFT].rolling(window=window_size, center=True).median()
        self.smoothed_data[self.arq_columns.CARIGHT] = self.data[self.arq_columns.CARIGHT].rolling(window=window_size, center=True).median()
        self.smoothed_data[self.arq_columns.TIME] = self.data[self.arq_columns.TIME]


    def dataFilter(self, methodology, **kwargs):
        '''
        Aplying data filtering following a give methodology
        '''
        if methodology == 'mean_filter':
            self.mean_filter(**kwargs)
            return

        if methodology == 'median_filter':
            self.median_filter(**kwargs)
            return

        if methodology == 'fourier_transform':
            raise Exception('Not yet implemented')
            # self.fourier_transform()
            return

        raise Exception(f'Metodologia {methodology} não válida')

    def plotData(self):
        '''
        method to plot the data
        '''
        fig, ax = plt.subplots()
        x = self.data[self.arq_columns.TIME]
        y = self.data[self.arq_columns.CA_MEAN]
        ax.plot(x,y)
        pass

    def plotFilteredData(self):
        '''
        method to plot the data
        '''
        fig, ax = plt.subplots()
        x = self.smoothed_data[self.arq_columns.TIME]
        y = self.smoothed_data[self.arq_columns.CA_MEAN]
        x_original = self.data[self.arq_columns.TIME]
        y_original = self.data[self.arq_columns.CA_MEAN]
        ax.plot(x,y, label = 'Filtrados')
        ax.plot(x_original,y_original, label = 'Originais', alpha=0.3)
        ax.set_xlabel('Tempo (s)')
        ax.set_ylabel('Ângulo de Contato Médio [°]')
        ax.legend()

        return fig, ax

    def exportFilteredData(self, arquive = 'smoothed_data.xlsx'):
        '''
        Creates a pd  dataframe and save it as an .xlsx file
        '''
        df = pd.DataFrame(self.smoothed_data)
        df = df[df[self.arq_columns.CA_MEAN].apply(lambda x: bool(x*2 == x + x))] # gambiarra para retirar o NaN
        df.to_excel(arquive)

# %%
