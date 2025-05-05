import yaml
import pandas as pd
import sys
from pathlib import Path
from ijazz.RegionalFitter import RegionalFitter
from ijazz.sas_utils import parameters_to_json, parameters_from_json
from ijazz.ScaleAndSmearing import categorize
from cms.common import get_file_name
import cms_fstyle
import matplotlib.pyplot as plt
import tensorflow as tf
import argparse
import numpy as np
import os
import re


def step_prototype(step_name:str, func_proto, config=None, **kwargs):
    help_msg = f"""ijazz_time_equalisation_{step_name.lower()} config
    where the config yaml file should have the following variables
    ------------------------------
    {func_proto.__doc__}
    """
    if not config:
        parser = argparse.ArgumentParser(description=f'IJazZ time equalisation {step_name}', usage=help_msg)
        parser.add_argument('config', type=str, help='yaml config file')
        for k, v in kwargs.items():
            parser.add_argument(f'--{k}', type=type(v), default=v)
        args = parser.parse_args(sys.argv[1:])
    
        print(f'{step_name} of IJazZ time equalisation using config file: {args.config}')
        with open(args.config, 'r') as f_yaml:
            config = yaml.safe_load(f_yaml)

        for k, v in kwargs.items():
            kwargs[k] = getattr(args, k)
    func_proto(**config['time_equalisation'], **kwargs, **config['reader'])   

def step0(config=None):
    step_prototype("STEP0", get_run_split,config=config)

def step1(config=None):
    step_prototype("STEP1", time_equalisation_fit,config=config, irun=1, nrun=-1)

def step2(config=None):
    step_prototype("STEP2", aggregate_time_equalisation_fit,config=config)

# ----------------------------------------------
# --- Actual functions implementation
# ----------------------------------------------
def get_run_split(file_dt:str=None, n_split: float=5e4, d_fsplit=0.2, dir_results='.', dset_id='Unknown', name_run='run', 
                  cfg_sas: dict=None,   **cfg_reader):
    """Function saving the run splitting to a csv file (this is step0 of time equalisation)

    Args:
        file_dt (str, optional): input file for data (can be inferred from reader if None). Defaults to None.
        n_split (float, optional): number of event in each subsample. Defaults to 5e4.
        d_fsplit (float, optional): tolerance w/r to n_plit (in percent). Defaults to 0.2.
        dir_results (str, optional):  directory to save the results. Defaults to '.'.
        name_run (str, optional): name of the run variable in file_dt. Defaults to 'run'.
        cfg_sas (dict, optional): dictionnary with the sas config. Defaults to None.
    """
    name_mll = cfg_sas['fitter'].get('name_mll', 'mass')

    # -- read the data file
    dt = pd.read_parquet(get_file_name(file_dt, cfg_reader, is_mc=False))

    # -- get the run splitting
    runs = split_run(dt, n_split=float(n_split), delta_f=float(d_fsplit), name_mll=name_mll, name_run=name_run)
    
    dir_results = Path(dir_results)
    dir_results.mkdir(parents=True, exist_ok=True)
    print(os.getcwd())
    print(f'Saving run split to file: {dir_results}/runs_{dset_id}.csv')
    runs.to_csv(dir_results / f'runs_{dset_id}.csv', index=False)


def time_equalisation_fit(file_dt:str=None, file_mc:str =None, dir_results='.', dset_id='Unknown', name_run='run', 
                          cfg_sas: dict=None, irun=0, nrun=-1, columns=None, name_mll='mass',  **cfg_reader):
    """Function fitting the scale in each run range (step 1 of time equalisation)
    Args:
        file_dt (str, optional): input file for data (can be inferred from reader if None). Defaults to None.
        file_mc (str, optional): input file for MC (can be inferred from reader if None). Defaults to None.
        dir_results (str, optional): directory to save the results. Defaults to '.'.
        dset_id (str, optional): dataset id. Defaults to 'Unknown'.
        name_run (str, optional): _description_. Defaults to 'run'.
        cfg_sas (dict, optional): dictionnary of the sas config. Defaults to None.
        irun (int, optional): first run to fit. Defaults to 0.
        nrun (int, optional): number of runs to fit. Defaults to -1.
        columns (list, optional): list of columns to read from the data file. Defaults to None (automatic).
        name_mll (str, optional): name of the dilepton mass. Defaults to 'mass'.
    """
    dir_results = Path(dir_results)
    cut = cfg_sas['sas'].get('cut', '')
    categories = cfg_sas['sas']['categories']
    name_weights = cfg_sas['fitter'].get('name_weights', 'weight_central')
    
    # get list of all the needed variables
    if columns is  None and cut:
        # add variables from the cut
        variables = set(re.findall(r"[a-zA-Z_]\w*", cut)) 
        operators = {"and", "or", "not"}
        variables = variables - operators
        columns = list(variables)
        # add the run and mass
        columns += [name_run, name_mll]
        # add variables from the categories
        columns += [f'{key}{num}' for key in categories.keys() for num in [1, 2]]

    if columns is not None or cut:
        columns_mc = columns + [name_weights]
    else:
        columns_mc = None
        
    # -- read the data/MC file
    dt = pd.read_parquet(get_file_name(file_dt, cfg_reader=cfg_reader, is_mc=False),columns=columns).reset_index(drop=True)
    mc = pd.read_parquet(get_file_name(file_mc, cfg_reader=cfg_reader, is_mc=True),columns=columns_mc).reset_index(drop=True)
    runs = pd.read_csv(dir_results / f'runs_{dset_id}.csv')

    # -- compute the scale manually to not redo the categorization each time
    for df in [dt, mc]:
        categorize(df, categories, cut=cut)

    learning_rate = cfg_sas.get('learning_rate', 1e-3)
    optimizer = tf.keras.optimizers.Adam
    hess = cfg_sas['sas'].get('hess', False)
    if hess:
        numerical = True if hess == 'numerical' else False
    
    # -- make the fits
    dir_results = dir_results / 'jsons'
    dir_results.mkdir(parents=True, exist_ok=True) 
    ntot = runs.shape[0]
    irun = max(0, irun)
    frun = min(ntot, irun + nrun)
    if frun < irun:
        frun = ntot 
    for run_min, run_max, _ in runs.iloc[irun:frun].itertuples(index=False):
        print(f"RUN-RANGE: {run_min} - {run_max}")
        dt_runs = dt.query(f"@run_min < {name_run} < @run_max").copy()
        fitter = RegionalFitter(dt_runs, mc, **cfg_sas['fitter'])
        fitter.minimize(optimizer(learning_rate=learning_rate), **cfg_sas['minimizer'])
        if hess:
            print(f"  --> HESSIAN: {hess}  numerical {numerical}")
            fitter.covariance(numerical=numerical, batch_size=-1)
        parameters_to_json({"categories": categories, "resp": fitter.resp, "reso": fitter.reso,
                            "eresp": fitter.eresp, "ereso": fitter.ereso, 
                            "eresp_mc": np.zeros(fitter.resp.shape), "ereso_mc": np.zeros(fitter.resp.shape)},
                            dir_results / f"SAS_time_equalisation_{run_min}-{run_max}.json")
        del dt_runs

def get_time_resp_reso_bins(runs, dir_jsons):
    """Get the time dependent response and resolution from the json files
    Args:
        runs (pd.DataFrame): run ranges
        dir_jsons (Path): directory with the json files
    Returns:
        time_resp (list): list of time dependent response
        time_reso (list): list of time dependent resolution
        bins (np.ndarray): bin edges
    """
    time_resp = []
    time_reso = []
    index = []
    for run_min, run_max, _ in runs.itertuples(index=False):
        try:
            pars = parameters_from_json( dir_jsons / f"SAS_time_equalisation_{run_min}-{run_max}.json")
            index.append(0.5*(run_min+run_max))
        except:
            continue
        bins = pars['bins'][0].numpy()
        if np.isnan(pars['resp'].numpy()).sum():
            print(f"WARNING: NaN values in SAS_time_equalisation_{run_min}-{run_max}.json")
        time_resp.append(np.nan_to_num(pars['resp'].numpy(),nan=1.0))
        time_reso.append(np.nan_to_num(pars['reso'].numpy(),nan=1.0))
    return time_resp, time_reso, bins

def plot_time_dep_resp_reso(time_param, bins, runs, y_range=(0.92, 1.05), run_split=None, eras=None, run_split_y=0.925, save_fig=None, delta=0.05):
    """Plot the time dependent response or resolution
    Args:
        time_param (pd.DataFrame): time dependent response or resolution
        bins (np.ndarray): bin edges
        runs (pd.DataFrame): runs csv
        y_range (tuple, optional): y range for the plot. Defaults to (0.92, 1.05).
        run_split (list, optional): list of run split values. Defaults to None.
        eras (list, optional): list of eras for the run split. Defaults to None.
        run_split_y (float, optional): y position for the run split text. Defaults to 0.925.
        save_fig (str, optional): file name to save the figure. Defaults to None.
        delta (float, optional): fraction of extra space to add to the x-axis. Defaults to 0.05.
    """
    columns =  [float(f'{b:.3f}') for b in 0.5*(bins[1:] + bins[:-1])]
    labels =  [f'[{b1:.1f},{b0:.1f}]' for b0, b1 in zip(bins[1:], bins[:-1])]
    col_to_label = dict(zip(columns, labels))
    index = [int(b) for b in 0.5*(runs['run_max']+runs['run_min'])]
    time_param = pd.DataFrame(time_param, columns=columns, index=index)
    
    cols = time_param.columns 
    cols[(-3.00 < cols) &  (cols < -1.49)]
    eem = cols[(-3.00 < cols) & (cols < -1.49)]
    ebm = cols[(-1.49 < cols) & (cols < -0.00)]
    ebp = cols[(+0.00 < cols) & (cols < +1.49)]
    eep = cols[(+1.49 < cols) & (cols < +3.00)]
    fig, ax = plt.subplots(2, 2, figsize=(10, 8), sharex=True, sharey=True)
    ax = ax.flatten()
    ecal_str = ["EB-", "EB+", "EE-", "EE+"]
    for iecal, ecal in enumerate([ebm, ebp, eem, eep]):
        if len(time_param[ecal].columns):
            if '-' in ecal_str[iecal]:
                time_param[ecal].iloc[:, ::-1].plot(marker='.', ylim=y_range, ax=ax[iecal], rot=45,ls='')
            else:    
                time_param[ecal].plot(marker='.', ylim=y_range, ax=ax[iecal], rot=45,ls='')
            # time_param[ecal].plot(marker='.', ylim=(0.99, 1.015), ax=ax[iecal], rot=45)
            ecal_labels = [col_to_label[col] for col in ecal]
            if '-' in ecal_str[iecal]:
                ecal_labels = ecal_labels[::-1]
            ax[iecal].legend(ecal_labels, ncols=2, title=f"{ecal_str[iecal]} ; $\eta$",fontsize='small')
    x1, x2 = ax[0].get_xlim()
    delta = (x2-x1)*delta
    if run_split is not None:
        for i,split in enumerate(run_split):
            for axx in ax:
                if split < x1-delta or split > x2+delta:
                    continue
                axx.axvline(split, ls='--', color='grey')
                axx.text(split+100, run_split_y, eras[i])

    cms_fstyle.polish_axis(ax[0], y_title='resp', x_range=(x1-delta, x2+delta))
    cms_fstyle.polish_axis(ax[2], y_title='resp', x_range=(x1-delta, x2+delta))
    
    if save_fig is not None:
        fig.savefig(save_fig)
        print(save_fig)

    return time_param


def aggregate_time_equalisation_fit(file_dt:str=None, dir_results='.', dset_id='Unknown', cset_version=1, name_run='run', name_eta='ScEta', correct_data=True,
                                    resp_range=(0.92, 1.05), reso_range=(0, 0.09), run_split=None, eras=None, **cfg_reader):
    """Aggregate the result from the run dependent scale fit into a single correction lib file

    Args:
        file_dt (str, optional): _description_. Defaults to None.
        dir_results (str, optional): _description_. Defaults to '.'.
        dset_id (str, optional): _description_. Defaults to 'Unknown'.
        cset_version (int, optional): _description_. Defaults to 1.
        name_run (str, optional): _description_. Defaults to 'run'.
        name_eta (str, optional): _description_. Defaults to 'ScEta'.
        correct_data (bool, optional): apply the scale to data. Defaults to True.
        resp_range (tuple, optional): y-range for resp plotting. Defaults to (0.92, 1.05).
        reso_range (tuple, optional): y-range for reso plotting. Defaults to (0, 0.09).
        run_split (list, optional): list with the starting run number of each eras. Defaults to None.
        eras (list, optional): list of each eras name. Defaults to None.
    """

    dir_results = Path(dir_results)
    runs = pd.read_csv(dir_results / f'runs_{dset_id}.csv')
    dir_jsons = dir_results  / 'jsons'
    
    time_resp, time_reso, bins = get_time_resp_reso_bins(runs, dir_jsons)
    # - scale plot
    time_resp = plot_time_dep_resp_reso(time_resp, bins, runs, y_range=resp_range,run_split=run_split, run_split_y=resp_range[0]+0.005, eras=eras, save_fig=f'{dir_results}/time_correction_resp_{dset_id}.jpg')
    # - resolution plot
    time_reso = plot_time_dep_resp_reso(time_reso, bins, runs, y_range=reso_range,run_split=run_split, run_split_y=0.055 ,eras=eras, save_fig=f'{dir_results}/time_correction_reso_{dset_id}.jpg')

    # -- save the result in a correction lib file
    import correctionlib.schemav2 as cs
    import rich
    cresp_time_dep = cs.Correction(
        name=f'EGMScaleVsRun_{dset_id}',
        version=cset_version,
        description=f"Time correction of the EM-energy Scale for dset {dset_id}",
        inputs=[cs.Variable(name=name_run, type="real", description="run number"),
                cs.Variable(name=name_eta, type="real", description="SuperCluster eta")],
        output=cs.Variable(name="scale", type="real", description="scale correction"),
        data=cs.MultiBinning(nodetype='multibinning', 
                            inputs=[name_run, name_eta],
                            edges=[[runs['run_min'].iloc[0]] + runs['run_max'].tolist(), bins],
                            content=1./time_resp.to_numpy().flatten(),
                            flow='clamp'),
    )
    rich.print(cresp_time_dep)
    cset_description = f"Scales and smearing for {dset_id}"
    cset_fileout = dir_results / f"EGMScalesSmearing_{dset_id}.v{cset_version}.json"
    cset = cs.CorrectionSet(
        schema_version=2,
        description=cset_description,
        corrections=[cresp_time_dep],
    )
    # -- check for NaN values
    if np.isnan(time_resp.to_numpy()).sum() > 0:
        print(f"WARNING: NAN in the correction: {np.isnan(time_resp.to_numpy()).sum()} NaN values")
    import gzip
    with gzip.open(f"{cset_fileout}.gz", "wt") as fout:
        print(f"Writing out {cset_fileout}.gz")
        fout.write(cset.model_dump_json(indent=1,exclude_unset=True))
    
    # -- correct the data
    if correct_data:
        file_dt = get_file_name(file_dt, cfg_reader, is_mc=False)
        print(f"Time equalisation of {file_dt} --> {file_dt.with_suffix('.TimeCorr.parquet')}")
        dt = pd.read_parquet(file_dt)
        for i_ele in [1, 2]:
            corr = cresp_time_dep.to_evaluator().evaluate(dt[name_run], dt[f'{name_eta}{i_ele}'])
            dt[f'pt{i_ele}'] *= corr
            dt['mass'] *= np.sqrt(corr)
        
        dt.to_parquet(file_dt.with_suffix('.TimeCorr.parquet'), engine="auto")
    

def split_run(dt: pd.DataFrame, n_split: float=5e4, delta_f=0.2, name_mll='mass', name_run='run') -> pd.DataFrame:
    """Define the run splitting for the time equalisation

    Args:
        dt (pd.DataFrame): input dataframce containing the data
        n_split (float, optional): nevts at least for splitting. Defaults to 5e4.
        delta_f (float, optional): tolerance w/r to n_plit (in percent). Defaults to 0.2.
        name_mll (str, optional): name of the dilepton mass in dt. Defaults to 'mass'.
        name_run (str, optional): name of the run number in dt. Defaults to 'run'.

    Returns:
        pd.DataFrame: run split data frame
    """

    runs = dt.groupby(name_run)[name_mll].count().sort_index().cumsum()
    n_split = min(n_split, runs.iloc[-1])

    run0, _ = list(runs.iloc[[0]].items())[-1]
    split_runs = [run0-0.1]
    split_nevt = [0]
    stop = False
    while not stop:
        runs_m0 = runs.loc[runs > n_split]
        run_stop, n_evt = -1, 0
        
        if len(runs_m0) > 0:
            run_stop, n_evt = list(runs_m0.iloc[[0]].items())[-1]
        else:
            # last batch has not enough stat
            run_stop, n_evt = list(runs.iloc[[-1]].items())[-1]
            # if not too far add a split otherwise add to previous split
            if n_evt > n_split*(1-delta_f):
                split_runs.append(run_stop + 0.1)
                split_nevt.append(n_evt)
            else:
                split_runs[-1] = run_stop + 0.1
                split_nevt[-1] += n_evt
            stop = True
            break
        
        run_stop_m1 , n_evt_m1 = -1, 0
        runs_m1 = runs.loc[runs.index < run_stop]
        if len(runs_m1) > 0:
            run_stop_m1 , n_evt_m1 = list(runs_m1.iloc[[-1]].items())[-1]
            
        if n_evt > n_split*(1+delta_f) and run_stop_m1 > 0:
            # -- if too many event try to stop just before
            if n_evt_m1 > n_split*(1-delta_f):
                run_stop, n_evt = run_stop_m1, n_evt_m1
                
        split_runs.append(run_stop + 0.1)
        split_nevt.append(n_evt)
        runs = runs[runs.index > run_stop] - n_evt
        stop = True if len(runs) == 0 else False

    runs = pd.DataFrame({'run_max': split_runs, 'nevt': split_nevt})
    runs['run_min'] =  runs['run_max'].shift(+1)
    runs = runs[['run_min', 'run_max', 'nevt']].fillna(1)[1:]

    return runs



