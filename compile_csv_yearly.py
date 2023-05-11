from os import path, listdir
import pandas as pd
Path = path.abspath('./csv_split_yearly/')
i = 0
files = listdir(Path)
files.sort()
print(files)
for file in files:
    if file[-3:] == 'csv' and i == 0:
        dict1 = pd.read_csv(path.join(Path,file), low_memory = False)
        # dict1.drop(['geometry','tests','devices','DAUID','PRUID','CDUID','CCSUID','CCSNAME','CSDUID','ERUID','SACCODE','CMAUID','CMAPUID','CMANAME','CMATYPE','CTUID','CTNAME','ADAUID','PCUID','PCPUID'], axis = 1)
        i += 1
    elif file[-3:] == 'csv' and i != 0:
        dict2 = pd.read_csv((path.join(Path,file)), low_memory = False)
        # dict2.drop(['geometry','tests','devices','DAUID','PRUID','CDUID','CCSUID','CCSNAME','CSDUID','ERUID','SACCODE','CMAUID','CMAPUID','CMANAME','CMATYPE','CTUID','CTNAME','ADAUID','PCUID','PCPUID'], axis = 1)
        dict1 = pd.concat([dict1, dict2], axis = 1)
dict1.to_csv('final_yearly.csv', index = False)