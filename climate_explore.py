import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as nc

dataframe1 = "/work2/ola/input/ERA5/grl16/grl16_ERA5_2005.nc"
dataframe2 = "/work2/ola/gitfiles/yelmox/output/ERA5_1991-2020/yelmo2D.nc"
df1 = nc.Dataset(dataframe1)
df2 = nc.Dataset(dataframe2)

tp = df1['tp'][:,:,:]
ice = df2['H_ice'][1,:,:]
smb = df2['smb'][1,:,:]


tp = np.sum(tp, axis=0)
tp = np.where(ice > 0, tp, 0)

smb = np.where(ice > 0, smb, 0)

print('SMB (50,130)')
print(smb[130,50])
print('TP (50,130)')
print(tp[130,50])



plt.figure(1)
plt.imshow(tp, cmap="nipy_spectral_r", origin="lower")
plt.title("Totalt precipitation 2005")
cb = plt.colorbar()
cb.set_label('mm')

plt.figure(2)
plt.imshow(smb, cmap="RdBu", origin="lower", vmin=-5, vmax=3)
plt.title("Smb 2005")
cb = plt.colorbar()
cb.set_label('m/a')
plt.show()

