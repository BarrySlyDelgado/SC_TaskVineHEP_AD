import matplotlib.pyplot as plt
import scipy

cores = 12
apps = {'DV3 Large':{10:[1327.413743019104], 
                     20:[546.1645128726959], 
                     50:[485.0281150341034], 
                     100:[289.08009696006775], 
                     200:[271.9908480644226]},
                     p
                    'RSTriPhoton':{20:[1601.6858911514282],
                     50:[1339.1242170333862],
                     100:[1156.3288300037384],
                     200:[1002.337464094162]
                     }}

                 

fig, axs = plt.subplots(1, 1, squeeze=False)


ax = axs[0][0]
info = {'x':[], 'y':[], 'yerr':[]}
for job_count in apps['DV3 Large']:
    info['x'].append(job_count*12),
    info['y'].append(sum(apps['DV3 Large'][job_count])/len(apps['DV3 Large'][job_count]))
ax.plot(info['x'], info['y'], color='darkgreen', linestyle='-', label='TaskVine DV3-Large')
info = {'x':[], 'y':[], 'yerr':[]}
for job_count in apps['RSTriPhoton']:
    info['x'].append(job_count*12),
    info['y'].append(sum(apps['RSTriPhoton'][job_count])/len(apps['RSTriPhoton'][job_count]))
ax.plot(info['x'], info['y'], color='darkblue', linestyle='-.', label='TaskVine RS-TriPhoton')
ax.set_ylabel('Execution Time (s)',fontsize=12)
ax.set_xlabel('Cores', fontsize=12)
ax.set_ylim(top=2000)
ax.legend()
ax.set_ylim(bottom=0)

width = 6.4 * 1
height = 4.8 * 1
fig.set_size_inches(w=width, h=height)
fig.savefig('graphs/ScalesLarge.pdf')


