import os
import hashlib
import math

import json
# import cloudpickle as pickle

import dask
from ndcctools.taskvine import DaskVine
import ndcctools.taskvine as vine

import awkward as ak
import dask_awkward as dak

top_dir = os.path.dirname(os.path.abspath(__file__))

# Get filenames from DAS and copy them to local directory
all_datasets = [
    # GJets 2016 APV
    "/GJets_HT-40To100_TuneCP5_13TeV-madgraphMLM-pythia8/RunIISummer20UL16NanoAODAPVv9-106X_mcRun2_asymptotic_preVFP_v11-v1/NANOAODSIM",
]

data_tags = ['DoubleEG', 'EGamma']

years = ["2016"]

mc_years_dict = {"2016":"RunIISummer20UL16"}

def get_year(dataset):
    if any(tag in dataset for tag in data_tags):
        for year in years:
            if year in dataset:
                return year
    else:
        for year, mc_year in mc_years_dict.items():
            if mc_year in dataset:
                return year
    raise ValueError(f"Dataset {dataset} not recognized as data or MC")

triggers= {"2016": ['DoublePhoton60'],
           "2017": [
               'DoublePhoton70', 
                "TriplePhoton_20_20_20_CaloIdLV2_R9IdVL"
                ],
           "2018": [
               'DoublePhoton70',
               "TriplePhoton_20_20_20_CaloIdLV2_R9IdVL"
               ]}

vast_base = "data"

def dataset_dir(dataset, base_dir, data_format):

    if any(tag in dataset for tag in data_tags):
        tag = "data"
    else:
        tag = "mc"
    
    outdir = f"{base_dir}/{tag}/{data_format}"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    return outdir

def get_dataset_name(das_dataset):
    return "_".join(das_dataset.split("/")[1:-1])

def get_filesets(datasets, base_dir, data_format, test=False, n_test_files=None):

    filesets = {}
    for dataset in datasets:
        filesets[dataset] = {}
        data_dir = dataset_dir(dataset, base_dir, data_format)
        files = [f for f in os.listdir(data_dir) if dataset in f]
        if test: files = files[:n_test_files]
        filesets[dataset]['files'] = {
            f"{data_dir}/{f}": {
                'object_path': "Events",
                } for f in files}
        filesets[dataset]['metadata'] = {'year': get_year(dataset)}

    return filesets

def do_preprocessing(
    datasets,
    step_size,
    input_base_dir=vast_base,
    input_format="NanoAODv9",
    reprocess=False,
    test=False,
    n_test_files=None,
    n_test_steps=None,
    scheduler=None):

    if test:
        print(f"Running in test mode with step size {step_size}")
        if n_test_files is not None:
            print(f"Only processing {n_test_files} files for each dataset")
        if n_test_steps is not None:
            print(f"Only processing {n_test_steps} steps for each file")

    def cache_path(dataset):
        cache_dir = f"{top_dir}/cache/preprocessing"
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        ftag = f"{dataset}_{step_size}"
        if test and n_test_files is not None:
            ftag += f"{n_test_files}files"
        return f"{cache_dir}/{ftag}.json"

    need_to_preprocess = []
    filesets = {}
    for dataset in datasets:
        preprocessing_cache = cache_path(dataset)
        if not os.path.exists(preprocessing_cache) or reprocess:
            need_to_preprocess.append(dataset)
        else:
            filesets[dataset] = json.load(open(preprocessing_cache))

    if need_to_preprocess:
        print(f'Preprocessing {len(need_to_preprocess)} datasets with chunk size {step_size}')
        print(need_to_preprocess)
        print(input_base_dir)
        filesets = get_filesets(need_to_preprocess, input_base_dir, input_format, test=test, n_test_files=n_test_files)
        from coffea.dataset_tools import preprocess
        available_fileset, _ = preprocess(
            filesets,
            step_size=step_size,
            skip_bad_files=True,
            save_form=True,
            scheduler=scheduler,
        )
        for dataset, info in available_fileset.items():
            filesets[dataset] = info
            json.dump(
                info,
                open(cache_path(dataset), 'w'),
                indent=4, separators=(',', ':'))

    if test and n_test_steps is not None:
        from coffea.dataset_tools import max_chunks
        filesets = max_chunks(filesets, n_test_steps)

    from coffea.dataset_tools import filter_files
    return filter_files(filesets)

def skim_dataset(dataset, dataset_info):
    from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
    from coffea.util import decompress_form

    events = NanoEventsFactory.from_root(
        dataset_info['files'],
        schemaclass=NanoAODSchema,
        known_base_form=ak.forms.from_json(decompress_form(dataset_info['form']))
    ).events()

    year = get_year(dataset)
    pass_trigger = dak.zeros_like(events.run, dtype='bool')
    for trigger in triggers[year]:
        pass_trigger = pass_trigger | events.HLT[trigger]

    good_photons = (events.Photon.cutBased >= 1) #& (events.Photon.pt > 20)
    # good_photons = (events.Photon.pt > 20)
    has_3_photons = dak.num(events.Photon[good_photons]) >= 3
    
    return events[pass_trigger&has_3_photons]

def compute_and_write(events, outpath):
    ak.to_parquet(dask.compute(events)[0], outpath)
def partition_to_parquet(partition, outpath):
    ak.to_parquet(partition, outpath)
    return outpath
def read_and_merge(*files, outpath, final=False):
    dfs = [ak.from_parquet(filename) for filename in files]
    df = ak.concatenate(dfs)
    ak.to_parquet(df, outpath)
    if not final:
        return outpath
def create_graph(filesets, output_base_dir=vast_base):
    graph = {}
    for dataset, info in filesets.items():
        events = skim_dataset(dataset, info)
        parquet_subsets = []
        npartitions = events.npartitions
        partition_chunk_size = 2
        steps = math.ceil(npartitions/partition_chunk_size)
        for i in range(steps):
            partition = events.partitions[i*partition_chunk_size:(i+1)*partition_chunk_size]
            outpath = f"{dataset_dir(dataset, output_base_dir, 'skim')}/{dataset}-{npartitions}-{steps}-{i+1}.parquet"
            graph[f"{dataset}-{npartitions}-{steps}-{i+1}"] = dask.delayed(partition_to_parquet)(partition, outpath)
            parquet_subsets.append([graph[f"{dataset}-{npartitions}-{steps}-{i+1}"], f"{dataset}-{npartitions}-{steps}-{i+1}"])
        while len(parquet_subsets) > 1:
            subsets = [parquet_subsets.pop(0) for _ in range(partition_chunk_size) if parquet_subsets]
            subset_futures = [x[0] for x in subsets]
            subset_names = [x[1] for x in subsets]
            if parquet_subsets:
                name = '-'.join(subset_names)
                hashstring = hashlib.md5(name.encode())
                outfile = hashstring.hexdigest()
                final = False
            else:
                outfile = dataset
                final = True
            outpath = f"{dataset_dir(dataset, output_base_dir, 'skim')}/{outfile}.parquet"
            subset_futures = tuple(subset_futures)
            graph[outfile] = dask.delayed(read_and_merge)(subset_futures, outpath=outpath, final=final)
            parquet_subsets.append([graph[outfile], outfile])
    return graph

def optimize_graph(graph):
    """A graph here is a dictionary of delayed object"""
    from dask.optimization import cull, fuse, inline
    from dask.delayed import Delayed
    new_graph = {}
    for key, delayed_obj in graph.items():
        dsk, _ = cull(delayed_obj.dask, delayed_obj.__dask_keys__())
        dsk, _ = fuse(dsk, ave_width=4)
        dsk = inline(dsk, delayed_obj.__dask_keys__())
        dsk, _ = cull(dsk, delayed_obj.__dask_keys__())
        new_graph[key] = Delayed(delayed_obj.__dask_keys__(), dsk)
    
    return new_graph

def compute_graph(graph, scheduler=None):
    if scheduler is not None:
        dask.compute(
            graph,
            scheduler=scheduler,
            task_mode='function-calls', 
            lib_resources={"cores":4, "slots":4},
            resources_mode=None,
            lazy_transfers=True)
    else:
        dask.compute(graph)

if __name__ == "__main__":
    import argparse
    import time

    t_start = time.time()
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_tag', '-d', type=str, default=None, help='dataset tag')
    parser.add_argument('--do_all', '-a', action='store_true', help='process all datasets')
    parser.add_argument('--step_size', '-s', type=int, default=500000, help='Split input files into chunks of this number of events for processing')
    parser.add_argument('--reprocess', '-r', action='store_true', help='reprocess datasets')
    parser.add_argument('--recreate_graph', action='store_true', help='recreate task graph')
    parser.add_argument('--optimize', action='store_true', help='optimize task graph')
    parser.add_argument('--outdir_base', '-o', type=str, default="outputs", help='output directory')
    parser.add_argument('--use_dask_vine', '-dv', action='store_true', help='use DaskVine')
    parser.add_argument('--test', '-t', action='store_true', help='test mode')
    parser.add_argument('--test_step_size', type=int, default=50, help='chunk size for test mode')
    parser.add_argument('--n_test_datasets', type=int, default=2, help='number of datasets to process in test mode (-1=all)')
    parser.add_argument('--n_test_files', type=int, default=3, help='number of files to process in test mode (-1=all)')
    parser.add_argument('--n_test_steps', type=int, default=2, help='number of chunks to process in test mode (-1=all)')
    args = parser.parse_args()

    dataset_tag = args.dataset_tag
    do_all = args.do_all
    step_size = args.step_size
    reprocess = args.reprocess
    recreate_graph = args.recreate_graph
    optimize = args.optimize
    outdir_base = args.outdir_base
    use_dask_vine = args.use_dask_vine

    test = args.test
    n_test_datasets = None
    n_test_files = None
    n_test_steps = None

    if test:
        outdir_base = f"{outdir_base}/test"
        step_size = args.test_step_size
        n_test_datasets = args.n_test_datasets if args.n_test_datasets>0 else None
        n_test_files = args.n_test_files if args.n_test_files>0 else None
        n_test_steps = args.n_test_steps if args.n_test_steps>0 else None

    if not os.path.exists(outdir_base):
        os.makedirs(outdir_base)
    
    scheduler = None
    if use_dask_vine:
        print('Executing with DaskVine')
        m = DaskVine(9125, name="rstri-test", run_info_path="vine-run-info")
        scheduler = m.get

    # Get datasets
    assert not (dataset_tag is not None and do_all), "Cannot specify dataset tag and use --do_all"

    if dataset_tag is not None:
        datasets = [get_dataset_name(d) for d in all_datasets if dataset_tag in d]
    elif do_all:
        dataset_tag = "all"
        datasets = [get_dataset_name(d) for d in all_datasets]
    else:
        raise ValueError("Must specify dataset tag or use --do_all")

    if test:
        datasets = datasets[:n_test_datasets]

    # Create output directories and remove files if they exist
    for dataset in datasets:
        outdir = dataset_dir(dataset, outdir_base, 'skim')
        outfile = f"{outdir}/{dataset}.parquet"
        if os.path.exists(outfile): os.remove(outfile)

    # Get filesets
    t1 = time.time()
    filesets = do_preprocessing(
        datasets, step_size,
        reprocess=reprocess,
        scheduler=scheduler,
        test=test,
        n_test_files=n_test_files,
        n_test_steps=n_test_steps)
    print(f'Preprocessing executed in {(time.time()-t1)/60} minutes.')

    # Create task graph
    t1 = time.time()
    print('Creating task graph')
    graph = create_graph(filesets, outdir_base)
    print(f'Task graph created in {(time.time()-t1)/60} minutes.')

    if optimize:
        graph = optimize_graph(graph)

    # Compute and write outputs
    t1 = time.time()
    print('Computing and writing outputs')
    dask.visualize(graph, filename='graph.svg')
    try:
        compute_graph(graph, scheduler=scheduler)
    except ValueError:
        pass
    print(f'Outputs computed and written in {(time.time()-t1)/60} minutes.')

    print(f'Skimming {dataset_tag} datasets executed in {(time.time()-t_start)/60} minutes.')
