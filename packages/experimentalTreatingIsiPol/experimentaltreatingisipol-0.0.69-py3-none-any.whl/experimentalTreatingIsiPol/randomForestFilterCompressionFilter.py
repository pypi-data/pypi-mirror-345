# %%
import os
import pandas as pd
import shutil

def copy_file(source_path, destination_path):
    try:
        shutil.copy(source_path, destination_path)
        print(f"File copied successfully from {source_path} to {destination_path}")
    except FileNotFoundError:
        print(f"Source file {source_path} not found.")
    except PermissionError:
        print(f"Permission denied: Unable to copy to {destination_path}.")
    except Exception as e:
        print(f"An error occurred: {e}")


    # return the path of the local copy

def parsePathsArchive(path)->list[str]:
    '''
    parse the path of the archive to get the name of the archives
    '''
    with open(path, 'r', encoding='utf-8') as f:
        archives = f.readlines()

    for each_line in range(len(archives)):
        archives[each_line] = archives[each_line].replace('\n', '')
    return archives

def generateData(path, destiny_path):
    '''
    generate the data to be analysed
    '''
    archives = parsePathsArchive(path)
    for archive in archives:
        print(archive)
        copy_file(archive, destiny_path)


generateData(r'D:\Jonas\PostProcessingData\DataArquives\data_to_train_for_filter.txt', os.getcwd())

'''
Reading the coppied data
'''
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\..\..\src'))
import matplotlib.pyplot as plt
import copy


from experimentalTreatingIsiPol.main import MechanicalTestFittingLinear

dict_data = {}
exp_original = {}
id = 0
for each_file in os.listdir(os.getcwd()):
    if each_file.endswith('.csv') or each_file.endswith('.csv_OUTLIER'):
        try:
            d = MechanicalTestFittingLinear(docConfig='_pi', archive_name=each_file,
                                        verbose=False)
            exp_original[id] = {'obj' : copy.deepcopy(d), 'path' : each_file} # salvando dados originais
            d.new_x = (d.new_x - min(d.new_x))/(max(d.new_x)-min(d.new_x))
            d.new_y = (d.new_y - min(d.new_y))/(max(d.new_y)-min(d.new_y))

            dict_data[id] = d
            id += 1
        except Exception as e:
            d = MechanicalTestFittingLinear(docConfig='_tau', archive_name=each_file,
                                        verbose=False)
            exp_original[id] = {'obj' : copy.deepcopy(d), 'path' : each_file} # salvando dados originais


            d.new_x = (d.new_x - min(d.new_x))/(max(d.new_x)-min(d.new_x))
            d.new_y = (d.new_y - min(d.new_y))/(max(d.new_y)-min(d.new_y))

            dict_data[id] = d
            id += 1
        os.remove(each_file) # deletando arquivos após a leitura

# %%
'''
Anotando os dados
'''
import tkinter
import numpy as np

# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure

root = tkinter.Tk()
root.wm_title("Embedded in Tk")

fig = Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot()
x = exp_original[int(0)].new_x
y = exp_original[int(0)].new_y
ax.plot(x, y)
ax.set_xlabel("Deformação [mm/mm]")
ax.set_ylabel("Tensão [MPa]")

canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.draw()

# pack_toolbar=False will make it easier to use a layout manager later on.
toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
toolbar.update()

canvas.mpl_connect(
    "key_press_event", lambda event: print(f"you pressed {event.key}"))
canvas.mpl_connect("key_press_event", key_press_handler)

button_quit = tkinter.Button(master=root, text="Quit", command=root.destroy)

cut_point_dict = {}
id_tracker = []

def submit():
    cut_point_val = cut_point.get()
    print("Point Selected: " + cut_point_val)
    cut_point_dict[id_tracker[-1]] = cut_point_val
    change_plot(id_tracker[-1]+1)
    cut_point.set("")

def set_min():
    print("Mínimo Selecionado")
    cut_point.set(1)

cut_point = tkinter.StringVar()
name_entry = tkinter.Entry(root, textvariable=cut_point, font=('calibre', 10, 'normal'))
sub_btn = tkinter.Button(root, text='Submit', command=submit)
max_btn = tkinter.Button(root, text='Mínimo', command=set_min)

def change_plot(new_val):
    # retrieve frequency
    ax.clear()
    ax.set_xlabel("Deformação [mm/mm]")
    ax.set_ylabel("Tensão [MPa]")
    ax.set_title(f"Plot {new_val}/{len(exp_original)-1}")
    # update data
    x = exp_original[int(new_val)].new_x
    y = exp_original[int(new_val)].new_y
    ax.plot(x, y)
    id_tracker.append(int(new_val))

    # required to update canvas and attached toolbar!
    canvas.draw()

slider_update = tkinter.Scale(root, from_=0, to=len(exp_original.keys())-1, orient=tkinter.HORIZONTAL,
                              command=change_plot, label="Experimento")

# Define a callback function for mouse click events
def on_click(event):
    if event.inaxes is not None:
        print(f"Clicked at: ({event.xdata}, {event.ydata})")
        cut_point.set(f"{event.xdata:.6f}")

# Connect the callback function to the mouse click event
canvas.mpl_connect("button_press_event", on_click)

# Packing order is important. Widgets are processed sequentially and if there
# is no space left, because the window is too small, they are not displayed.
# The canvas is rather flexible in its size, so we pack it last which makes
# sure the UI controls are displayed as long as possible.
button_quit.pack(side=tkinter.BOTTOM)
slider_update.pack(side=tkinter.BOTTOM)
name_entry.pack(side=tkinter.BOTTOM)
sub_btn.pack(side=tkinter.BOTTOM)
max_btn.pack(side=tkinter.BOTTOM)

toolbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

tkinter.mainloop()

# %%
'''
Salvando dados anotados
'''
import pickle

# Example dictionary

teste = (dict_data, cut_point_dict)

# Save the dictionary to a file
with open('data_anotted_compression_filter.pkl', 'wb') as file:
    pickle.dump(teste, file)

print("data saved successfully!")
# %%

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\..\..\src'))
import matplotlib.pyplot as plt
import pickle

from experimentalTreatingIsiPol.main import MechanicalTestFittingLinear

# Open the serialized file
with open('data_anotted_compression_filter.pkl', 'rb') as file:
    loaded_dict = pickle.load(file)

print("Loaded dictionary:", loaded_dict)

# %%
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

# %%
'''
Preparando os dados (escalando para ficar na mesma dimensão)
'''
original_exp_data = loaded_dict[0]

# Finding the minum lenght for all the experiments

min_num_points = len(original_exp_data[0].new_x)
for index, each_data in original_exp_data.items():
    x_ = each_data.new_x
    min_num_points_ = len(x_)
    if min_num_points_ <= min_num_points:
        min_num_points = min_num_points_


dict_interpolated_data = {}

# Interpolate all points to get the same number of points
for index, each_data in original_exp_data.items():
    x_ = each_data.new_x
    y_ = each_data.new_y
    x_0 = min(x_)
    x_f = max(x_)
    x_interp = np.linspace(x_0, x_f, min_num_points)
    y_interp = np.interp(x_interp, x_, y_)
    dict_interpolated_data[index] = (x_interp, y_interp)


# %%
# Reshape the data to be used in the model
X = []
Y = []

anotted_data = loaded_dict[1]
for index, each_data in dict_interpolated_data.items():
    x_ = each_data[0]
    y_ = each_data[1]
    np.concatenate((x_, y_))
    if index in anotted_data.keys():
        X.append(np.concatenate((x_, y_)))
        Y.append(float(anotted_data[index]))
X = np.array(X)
Y = np.array(Y)/max(Y)

# %%
'''
Training the model
'''
# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

# Initialize the RandomForestRegressor
rf_regressor = RandomForestRegressor(n_estimators=100, random_state=42)

# Train the model
rf_regressor.fit(X_train, y_train)

# Make predictions on the test set
y_pred = rf_regressor.predict(X_test)
feature_size = int(X.shape[1]/2)
# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse}")



# %%
'''
Salvando o modelo treinado
'''

# Save the dictionary to a file
with open('randomForestModel_Compression.pkl', 'wb') as file:
    pickle.dump((rf_regressor, feature_size), file=file)

print("data saved successfully!")

# %%
'''
Testando o modelo em algumas situações
'''
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\..\..\src'))
import matplotlib.pyplot as plt
import pickle

from experimentalTreatingIsiPol.main import MechanicalTestFittingLinear
import matplotlib.pyplot as plt
import numpy as np
import pickle
print(os.getcwd())

# Save the dictionary to a file
with open(os.path.join(os.getcwd(),'randomForestModel_Compression.pkl'), 'rb') as file:
    model = pickle.load(file)


num_features = model[1]
trained_rf = model[0]

print("data loaded successfully!")

experimetal_data = exp_original[5]
x_original : list = experimetal_data.new_x
y_original : list = experimetal_data.new_y

x_original_bk = [x for x in x_original]
y_original_bk = [y for y in y_original]

# scaling the data

x_interp = np.linspace(min(x_original), max(x_original),num_features)
y_interp = np.interp(x_interp, x_original, y_original)

x_scaled = (x_interp - min(x_interp))/(max(x_interp)- min(x_interp))
y_scaled = (y_interp - min(y_interp))/(max(y_interp)- min(y_interp))

x_cut = trained_rf.predict([np.concatenate((x_scaled, y_scaled))])


fig, ax = plt.subplots()

ax.plot(x_original_bk, y_original_bk)
ax.axvline(x_cut[0]*max(x_original_bk))


# %%
cut_point_obj = {}
for each_obj, each_cut_point in zip(exp_original.keys(),cut_point_dict):
    cut_point_obj[exp_original[each_obj]['path']] = cut_point_dict[each_cut_point]

# Save the dictionary to a file
with open('cut_points.pkl', 'wb') as file:
    pickle.dump(cut_point_obj, file=file)
# %%
