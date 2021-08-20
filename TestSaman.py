# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 15:44:14 2020

@author: stavakoli
"""
import os
import shutil
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import flopy
import pyemu

model_ws = os.path.join('base_model_files')
print(os.listdir(model_ws))


mf = flopy.modflow.Modflow.load('freyberg.nam', model_ws = model_ws, verbose=True)

print(mf)

print(mf.dis)
print(mf.dis.top)
print(mf.rch.rech)
print(mf.bas6.strt)

print(mf.ghb.stress_period_data)

arr = mf.ghb.stress_period_data.array["bhead"]
cb = plt.imshow(arr[0,0,:,:]) # first time, first layer, all rows and columns
plt.colorbar(cb)

print(mf.rch.rech.array.shape)

pd.DataFrame.from_records(mf.sfr.reach_data).head()

# Exporting to Shapefiles
mf.export("model.shp")
mf.dis.export("dis.shp")
mf.dis.export("top.shp")
mf.ghb.stress_period_data.export("ghb.shp")

print(mf.modelgrid)

mf.change_model_ws("flopy_temp", reset_external= True)
mf.write_input()

print(os.listdir("bin"))

pyemu.os_utils.run("mfnwt freyberg.nam", cwd = mf.model_ws)

#Post_Porcessing
mflist = flopy.utils.MfListBudget(os.path.join(mf.model_ws,mf.name+".list"))
inc_df, cum_df = mflist.get_dataframes(start_datetime = "5-11-1995", diff = True)
print(inc_df)
inc_df.plot(kind="bar", figsize = (10,5))

hds = flopy.utils.HeadFile(os.path.join(mf.model_ws,mf.name+".hds"), model = mf)
print(hds.get_times())
print(hds.list_records())
data = hds.get_data()

hds.plot(mflay = None, totim = None, colorbar = True)

hds.to_shapefile("hds.shp")

cbc = flopy.utils.CellBudgetFile(os.path.join(mf.model_ws,mf.name+".cbc"))

print(cbc.list_records())

text = "flow right face"
times = cbc.get_times()
fig,axes = plt.subplots(mf.nlay,mf.nper,figsize = (10,10))

for kper in range(mf.nper):
    data = cbc.get_data(text= text, totim = times[kper], full3D=True)[0]
    data = np.ma.masked_where(mf.bas6.ibound.array<1,data)
    vmin,vmax = data.min(),data.max()
    
    for k in range(mf.nlay):
        cb = axes[k,kper].imshow(data[k,:,:],vmin = vmin, vmax = vmax)
        axes[k,kper].set_title("{0} , layer {1}, SP {2}".format(text,k+1,kper+1))
        plt.colorbar(cb,ax = axes[k,kper])

plt.tight_layout()
plt.show()









