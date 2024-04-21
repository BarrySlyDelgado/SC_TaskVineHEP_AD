import matplotlib.pyplot as plt
import scipy

cores = 12
conf_1 = {'Dask':{5:[10*60+8, 462.45, 10*60+8], 
                 10:[10*60+8, 10*60 + 45, 355.61], 
                 15:[325.83, 308.70, 13*60+9], 
                 20:[313.36, 10*60 + 8, 11*60+51], 
                 25:[10*60+21, 10*60 + 6, 10*60+7]},
                 
          'TaskVine':{5:[474.101, 441.9343020915985, 383.39267086982727], 
                      10:[338.3983190059662, 303.1359272003174, 328.9735379219055], 
                      15:[286.7015309333801,315.65843200683594, 284.4785261154175],
                      20:[280.46802592277527,487.0606589317322,268.92536091804504], 
                      25:[290.3308799266815,243.297180891037,336.80683612823486]}}
                 
conf_2 = {'Dask':{5:[23*60 + 20, 25*60 + 4, 14*60 + 49], 
                 10:[17*60 + 58, 12*60 + 32, 18*60 +38], 
                 15:[397, 17*60 + 14, 10*60 + 8], 
                 20:[13*60 + 20, 23*60 + 13, 10*60 + 23], 
                 25:[13*60 + 14, 12*60 + 21, 17*60 + 11]},
                 
          'TaskVine':{5:[1511.1378967761993, 1502.169532775879],
                      10:[802.5817708969116, 879.0789949893951, 842.020840883255], 
                      15:[620.0730350017548,614.7532589435577,652.3721210956573],
                      20:[510.084410905838,504.7925429344177,492.63020491600037],
                      25:[471.36351799964905,434.1821708679199,454.6567449569702]}}

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
info = {'x':[], 'y':[], 'yerr':[]}
for job_count in conf_2['Dask']:
    if not len(conf_2['Dask'][job_count]):
        continue
    info['x'].append(job_count*12),
    info['y'].append(sum(conf_2['Dask'][job_count])/len(conf_2['Dask'][job_count]))
    info['yerr'].append(scipy.stats.sem(conf_2['Dask'][job_count]))
ax.errorbar(info['x'], info['y'], info['yerr'], capsize=5, color='blue', linestyle='-.', label='Dask DV3-Medium')
info = {'x':[], 'y':[], 'yerr':[]}
for job_count in conf_2['TaskVine']:
    if not len(conf_2['TaskVine'][job_count]):
        continue
    info['x'].append(job_count*12),
    info['y'].append(sum(conf_2['TaskVine'][job_count])/len(conf_2['TaskVine'][job_count]))
    info['yerr'].append(scipy.stats.sem(conf_2['TaskVine'][job_count]))
ax.errorbar(info['x'], info['y'], info['yerr'], capsize=5, color='green', linestyle='-', label='TaskVine DV3-Medium')
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


