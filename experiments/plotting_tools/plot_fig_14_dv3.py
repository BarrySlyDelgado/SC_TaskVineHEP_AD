import matplotlib.pyplot as plt
import scipy

cores = 12
conf_1 = {'Dask':{5:[], 
                 10:[], 
                 
          'TaskVine':{5:[], 
                      10:[], 
fig, axs = plt.subplots(1, 1, squeeze=False)


ax = axs[0][0]
info = {'x':[], 'y':[], 'yerr':[]}
for job_count in conf_1['Dask']:
    info['x'].append(job_count*12),
    info['y'].append(sum(conf_1['Dask'][job_count])/len(conf_1['Dask'][job_count]))
    info['yerr'].append(scipy.stats.sem(conf_1['Dask'][job_count]))
ax.errorbar(info['x'], info['y'], info['yerr'], capsize=5, color='darkblue', linestyle=':', label='Dask DV3-Small')
info = {'x':[], 'y':[], 'yerr':[]}
for job_count in conf_1['TaskVine']:
    info['x'].append(job_count*12),
    info['y'].append(sum(conf_1['TaskVine'][job_count])/len(conf_1['TaskVine'][job_count]))
    info['yerr'].append(scipy.stats.sem(conf_1['TaskVine'][job_count]))
ax.errorbar(info['x'], info['y'], info['yerr'], capsize=5, color='darkgreen', linestyle='--', label='TaskVine DV3-Small')
ax.set_xticks(info['x'])
ax.set_ylabel('Execution Time (s)',fontsize=12)
ax.set_xlabel('Cores', fontsize=12)
ax.set_ylim(top=2000)
ax.legend()
ax.set_ylim(bottom=0)
#ax.set_xlim(left=0)
width = 6.4 * 1
height = 4.8 * 1
fig.set_size_inches(w=width, h=height)
fig.savefig('graphs/Scales.pdf')


