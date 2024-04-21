import matplotlib.pyplot as plt
import scipy

cores = 12
apps = {'DV3':{1:[], 
                     4:[], 
                    'RSTriPhoton':{1:[],
                     4:[]
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


