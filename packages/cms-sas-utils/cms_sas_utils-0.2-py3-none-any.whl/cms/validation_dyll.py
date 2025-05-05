import yaml
import argparse
import sys
from cms.common import fig_add_text, get_df_with_correction
import pandas as pd
from typing import Dict, List
import cms.plotting as ijp
import numpy as np
from pathlib import Path
from copy import deepcopy
from glob import glob



def get_mll_names(mll: str):
    if mll is None:
        return None, None, None
    else:
        mll = mll.split(':')
    if len(mll) == 3:
        mll_name, pt_name, name = mll
    elif len(mll) == 2:
        mll_name, name = mll
        pt_name = None
    elif len(mll) == 1:
        mll_name = mll[0]
        pt_name = None
        name = None
    else:
        raise ValueError(f'Wrong format for mll: {mll}. It should be "mll_name:pt_name:name" or "mll_name:name" or "mll_name"')
    
    return mll_name, pt_name, name

def validation_plot(dt: pd.DataFrame, mc: pd.DataFrame, cfg: Dict, dir_out=None, year=None, do_normalize=False):
    dir_out = Path(dir_out) if dir_out else Path('tmp')

    corr_path = Path(cfg.get('pattern_out', 'Unknown'))
    selection = cfg.get('selection', None)
    print(selection)
    sel_latex = cfg.get('selection_latex', [])
    mll1 = cfg.get('mll1', 'mass_raw:raw')
    mll_name1, pt_name1, name1 = get_mll_names(mll1)

    mll2 = cfg.get('mll2', None)
    mll_name2, pt_name2, name2 = get_mll_names(mll2)

    try:
        var_cats = cfg['regions']['bins']
        var_name = cfg['regions']['var_name']
        var_latex = cfg['regions'].get('var_latex', var_name)
    except KeyError:
        var_name = None
        var_cats = None
        var_latex = None

    
    mc_w_name = cfg.get("name_weights", None)
    year = cfg.get('year', year)
    plot_kwargs = cfg.get('plot_kwargs', {})

    df_dt, df_mc = (dt, mc)
    # if selection is not None:
    #     df_dt = dt.query(selection).copy()
    #     df_mc = mc.query(selection).copy()

    if do_normalize:
        if mc_w_name:
            norm = len(dt.query(f'80 < {mll_name1} < 100'))/(mc[0].query(f'80 < {mll_name1} < 100')[mc_w_name].sum())
            mc[0][mc_w_name] = mc[0][mc_w_name]*norm
        else:
            norm = len(dt.query(f'80 < {mll_name1} < 100'))/len(mc[0].query(f'80 < {mll_name1} < 100'))
            mc[0]['weight'] = norm
            mc_w_name = 'weight'
        print(f'Normalization factor: {norm}')



    dir_out.mkdir(exist_ok=True, parents=True)

    df_chi2s = []
    for is_diag, out_suffix, lepcat_name  in zip([False, True], ['incl', 'diag'], ['$Inclusive$', '$Diagonal$']):
        if var_name is None and is_diag:
            continue
        figs, (chi21, chi22),_ = ijp.plot_mll_data_per_cat(df_dt, df_mc, mll_name1=mll_name1, mll_name2=mll_name2, 
                                                         pt_name1=pt_name1, pt_name2=pt_name2,
                                                         var_name=var_name, var_cats=var_cats, var_latex=var_latex,
                                                         mc_w_name=mc_w_name, cut0=selection, both_leptons=is_diag, 
                                                         **plot_kwargs)
        
        mll_bins = plot_kwargs.get('mll_bins', (80, 100, 81))
        for iax, corr_name in zip([0, 2], [name1, name2]):
            if corr_name is None:
                continue
            fig_add_text(figs, iax, lepcat_name, dy=0.90, fs=20, year=year, x_pos=mll_bins[0]+1)
            dy = 0.81
            for sel in sel_latex:
                fig_add_text(figs, iax, sel, dy=dy, fs=15, x_pos=mll_bins[0]+1)
                dy -= 0.08
            fig_add_text(figs, iax, corr_name, dy=dy-0.02, fs=20, x_pos=mll_bins[0]+1)

        for ifig, fig in enumerate(figs):
            out_file = dir_out / (corr_path.stem + f"_{out_suffix}_fig{ifig}.jpg")
            print(f'Saving file {out_file}')
            fig.savefig(out_file)
        if mll_name2:
            df_chi2s.append(pd.DataFrame({'chi2_1': chi21, 'chi2_2': chi22, 'ifig': np.arange(len(figs))}).assign(name=corr_path.stem + f"_{out_suffix}"))
        else:
            df_chi2s.append(pd.DataFrame({'chi2_1': chi21, 'ifig': np.arange(len(figs))}).assign(name=corr_path.stem + f"_{out_suffix}"))
    return pd.concat(df_chi2s)

def validation_plot_EGM(dt: pd.DataFrame, mc: pd.DataFrame, cfg: Dict, dir_out=None, year=None):
    print("validation_plot_EGM")
    dir_out = Path(dir_out) if dir_out else Path('tmp')

    corr_path = Path(cfg.get('pattern_out', 'Unknown'))
    selection = cfg.get('selection', None)
    sel_latex = cfg.get('selection_latex', [])
    
    mll1 = cfg.get('mll1', 'mass_raw:raw')
    mll_name1, pt_name1, name1 = get_mll_names(mll1)

    mll2 = cfg.get('mll2', None)
    mll_name2, pt_name2, name2 = get_mll_names(mll2)

    try:
        var_cats = cfg['regions']['bins']
        var_name = cfg['regions']['var_name']
        var_latex = cfg['regions'].get('var_latex', var_name)
    except KeyError:
        var_name = None
        var_cats = None
        var_latex = None

    mll_nbins = cfg.get('mll_binning', (80, 100, 81))
    mc_w_name = cfg.get("name_weights", None)
    yr_range = cfg.get('yr_range', (0.8, 1.2))
    year = cfg.get('year', year)

    df_dt, df_mc = (dt, mc)

    dir_out.mkdir(exist_ok=True, parents=True)

    df_chi2s = []
    
    figs, (chi21, chi22), cat_legends, lists = ijp.plot_mll_data_per_cat(df_dt, df_mc, mll_name1=mll_name1, mll_name2=mll_name2, 
                                                            pt_name1=pt_name1, pt_name2=pt_name2,
                                                            var_name=var_name, var_cats=var_cats, var_latex=var_latex,
                                                            mc_w_name=mc_w_name, yr_range=yr_range, cut0=selection,
                                                            mll_bins=mll_nbins, lead_electron=True)

    for iax, corr_name in zip([0, 2], [name1, name2]):
        
        if corr_name is None:
            continue
        dy = 0.98
        if var_cats:
            dy -= 0.08*len(var_cats)
        fig_add_text(figs, iax, cat_legends, dy=dy, fs=15)
        dy -= 0.08
        for sel in sel_latex:
            fig_add_text(figs, iax, sel, dy=dy, fs=15)
            dy -= 0.08
        fig_add_text(figs, iax, corr_name, dy=dy-0.02, fs=20, year=year)

    for ifig, fig in enumerate(figs):
        if ifig % 5 or len(figs) == 1:
            out_file = dir_out / (corr_path.stem + f"_fig{ifig:02}.jpg")
            print(f'Saving file {out_file}')
            fig.savefig(out_file)
        # pd.DataFrame({'x_min': lists[0][ifig][0:-1], 'x_max': lists[0][ifig][1:], 'n_dt_ijazz': lists[1][ifig][0], 'n_mc_ijazz': lists[1][ifig][1], 'n_dt_egm': lists[2][ifig][0], 'n_mc_egm': lists[2][ifig][1]}).to_csv(dir_out / (corr_path.stem + f"_fig{ifig:02}.csv"))
    if mll_name2:
        df_chi2s.append(pd.DataFrame({'chi2_1': chi21, 'chi2_2': chi22, 'ifig': np.arange(len(figs))}).assign(name=corr_path.stem))
    else:
        df_chi2s.append(pd.DataFrame({'chi2_1': chi21, 'ifig': np.arange(len(figs))}).assign(name=corr_path.stem))
    
    return pd.concat(df_chi2s)


def kinematic_plot(dt: pd.DataFrame, mc: pd.DataFrame, cfg: Dict, dir_out=None, year=None, do_normalize=False):
    dir_out = Path(dir_out) if dir_out else Path('tmp')

    corr_path = Path(cfg.get('pattern_out', 'Unknown'))
    var_name = cfg.get('var_name', 'mass')

    if var_name not in dt.columns:
        print(f'Variable {var_name} not found in the data file')
        return None
    var_latex = cfg.get('var_latex', var_name)
    var_unit = cfg.get('var_unit', 'GeV')

    selection = cfg.get('selection', None)
    sel_latex = cfg.get('selection_latex', [])

    var_min, var_max, var_nbins = cfg.get('var_binning', (80, 100, 81))
    mc_w_name = cfg.get("name_weights", None)
    year = cfg.get('year', year)
    plot_kwargs = cfg.get('plot_kwargs', {})

    dir_out.mkdir(exist_ok=True, parents=True)

    if do_normalize:
        mll_name1 = 'mass'
        if mc_w_name:
            norm = len(dt.query(f'80 < {mll_name1} < 100'))/(mc[0].query(f'80 < {mll_name1} < 100')[mc_w_name].sum())
            mc[0][mc_w_name] = mc[0][mc_w_name]*norm
        else:
            norm = len(dt.query(f'80 < {mll_name1} < 100'))/len(mc[0].query(f'80 < {mll_name1} < 100'))
            mc[0]['weight'] = norm
            mc_w_name = 'weight'
        print(f'Normalization factor: {norm}')

    figs, (chi2,_), (mll_bins_out, hists) = ijp.plot_mll_data_per_cat(dt, mc, mc_w_name=mc_w_name, cut0=selection,
                                               mll_bins=np.linspace(var_min, var_max, var_nbins), mll_name1=var_name, 
                                               mll_latex=var_latex, mll_unit=var_unit, **plot_kwargs)
    
    fig_add_text(figs, 0, "", dy=0.90, fs=20, year=year)
    dy=0.90
    for isel, sel in enumerate(sel_latex):
        scale = 1.25 if isel == 0 else 1
        fig_add_text(figs, 0, sel, dx=0.05, dy=dy, fs=15)
        dy -= 0.07

    for ifig, fig in enumerate(figs):
        out_file = dir_out / corr_path
        print(f'Saving file {out_file}')
        # pd.DataFrame({'x_min': mll_bins_out[0:-1], 'x_max': mll_bins_out[1:], 'n_dt': hists[0], 'n_mc': hists[1], 'n_mc_weighted': hists[2]}).to_csv(dir_out / (corr_path.stem + f".csv"))
        fig.savefig(out_file)

    return pd.DataFrame({'chi2_1': chi2, 'ifig': np.arange(len(figs))}).assign(name=corr_path.stem)


def ijazz_kin_plot_cmd():
    parser = argparse.ArgumentParser(description=f'IJazZ kinematic plot tool')
    parser.add_argument('config_samples', type=str, help='yaml config file')
    parser.add_argument('--cfg', type=str, default=None, help='path to the yaml config with plots')
    args = parser.parse_args(sys.argv[1:])
    with open(args.config_samples, 'r') as fcfg:
        config = yaml.safe_load(fcfg)

    try: 
        with open(args.cfg, 'r') as fcfg:
            config_plot = yaml.safe_load(fcfg)['validation']
    except (FileNotFoundError, KeyError, TypeError):
        # plot config has not the right format, try directly the main config
        config_plot = config['validation']

    ijazz_kin_plot(config, config_plot)

def ijazz_kin_plot(config: Dict=None, config_plot: Dict=None):
    """Kinematic plot tool for SaS

    Args:
        config (Dict, optional): config file for samples and parameters. Defaults to None.
        config_plot (Dict, optional): config file defining the variables to plot. Defaults to None.
    """
            
    mll_name = config.get('mll_name', 'mass')

    dir_out = config.get('dir_results', 'tmp')
    year = config.get('year', None)

    print(f'Storing plots in dir: {dir_out}')

    df_dt = get_df_with_correction(config['file_dt'], mll_name=mll_name, is_mc=False, do_syst=False).reset_index(drop=True)
    df_mc = get_df_with_correction(config['file_mc'], mll_name=mll_name, is_mc=True)
    if isinstance(df_mc, list):
        df_mc = [df.reset_index(drop=True) for df in df_mc]
    else:
        df_mc = df_mc.reset_index(drop=True)

    
    df_chi2s = []
    for plot in config_plot:
        df_chi2s.append(kinematic_plot(df_dt, df_mc, plot, dir_out=dir_out, year=year))
    
    pd.concat(df_chi2s).to_csv(Path(dir_out) / 'chi2s_summary.csv')


def ijazz_mll_steps_plot():
    parser = argparse.ArgumentParser(description=f'IJazZ mll step by step plot tool')
    parser.add_argument('config_samples', type=str, help='yaml config file')
    parser.add_argument('--cfg', type=str, default=None, help='path to the yaml config with plots')
    args = parser.parse_args(sys.argv[1:])

    with open(args.config_samples, 'r') as fcfg:
        config = yaml.safe_load(fcfg)
    mll_name = config.get('mll_name', 'mass')

    dir_out = config.get('dir_results', 'tmp')
    year = config.get('year', None)

    print(f'Storing plots in dir: {dir_out}')
    
    try: 
        with open(args.cfg, 'r') as fcfg:
            config_plot = yaml.safe_load(fcfg)['validation']
    except (FileNotFoundError, KeyError, TypeError):
        # plot config has not the right format, try directly the main config
        config_plot = config['validation']

    try: 
        with open(args.cfg, 'r') as fcfg:
            steps = yaml.safe_load(fcfg)['steps']
    except (FileNotFoundError, KeyError, TypeError):
        # plot config has not the right format, try directly the main config
        steps = config['steps']

    files_dt = config['file_dt']
    files_mc = []

    for i,step in enumerate(steps):
        files_mc = []
        print(f'Processing step: {step["name_correction"]}')
        files_dt = [{**file, 'name': file['name'].replace('.parquet', f'.{step["name_correction"]}.parquet' if step["name_correction"] not in ["", "PhoEtaTimeCorr"] else '.parquet')} for file in files_dt]
        

        dir_out_step = Path(dir_out) / step["name_folder"] / "m_ll_plots"
        print(f'Storing plots in dir: {dir_out_step}')

        corrlib_smear = step.get('corrlib_smear', None)
        
        if corrlib_smear:
            for j,mcfile in enumerate(config['file_mc']):
                if len(corrlib_smear['corrlib_file']) > 1:
                    cfile = corrlib_smear['corrlib_file'][j]
                    cset = corrlib_smear['cset_name'][j]
                else:
                    cfile = corrlib_smear['corrlib_file'][0]
                    cset = corrlib_smear['cset_name'][0]
                corr_dict = {'path': cfile, 'cset_name': cset, 'cset_vars': corrlib_smear['cset_vars']}
                files_mc.append({**mcfile,'corrlib':corr_dict})
        else:
            files_mc = config['file_mc']
         
        df_dt = get_df_with_correction(files_dt, mll_name=mll_name, is_mc=False).reset_index(drop=True)
        df_mc = get_df_with_correction(files_mc, mll_name=mll_name, is_mc=True).reset_index(drop=True)
        

        for plot in config_plot:
            plot_cp = deepcopy(plot)
            selection_plot = plot.get('selection', None)
            selection_step = step.get('selection', None)
            if selection_plot and selection_step:
                plot_cp['selection'] = f"({selection_plot}) and ({selection_step})"
            else:
                plot_cp['selection'] = selection_plot or selection_step

            selection_latex_plot = plot.get('selection_latex', [])
            selection_latex_step = step.get('selection_latex', [])
            plot_cp['selection_latex'] =  selection_latex_step + selection_latex_plot
            kinematic_plot(df_dt, df_mc, plot_cp, dir_out=dir_out_step, year=year)


def ijazz_valid_plot(config: Dict=None, config_plot: Dict=None, syst: bool=False, add_mass: str='', AN: bool=False):
    """Validation plot tool for SaS
    Args:
        config (Dict, optional): config file for samples and parameters. Defaults to None.
        config_plot (Dict, optional): config file defining the categories to plot. Defaults to None.
        syst (bool, optional): add systematics. Defaults to False.
        add_mass (str, optional): variables and name of a second mass to add to the plot, eg mass_egm:pt_egm:EGM. Defaults to ''.
        AN (bool, optional): use AN mode, i.e. categories for lead only. Defaults to False.
    """
    import warnings
    warnings.filterwarnings("ignore")

    mll_name = config.get('mll_name', 'mee')
    year = config.get('year', None)
    dir_out = config.get('dir_results', 'tmp')
    print(f'Storing plots in dir: {dir_out}')

    df_dt = get_df_with_correction(config['file_dt'], mll_name=mll_name, is_mc=False, do_syst=False).reset_index(drop=True)
    df_mc = get_df_with_correction(config['file_mc'], mll_name=mll_name, is_mc=True, do_syst=syst)
    if isinstance(df_mc, list):
        df_mc = [df.reset_index(drop=True) for df in df_mc]
    else:
        df_mc = df_mc.reset_index(drop=True) 

    if isinstance(dir_out, list):
        selections = config.get('selection', None)
        for dir,selection in zip(dir_out, selections):
            df_chi2s = []
            for plot in config_plot:
                plot_cp = deepcopy(plot)
                if not plot_cp.get('mll2', None) and add_mass:
                    plot_cp['mll2'] = add_mass
                    
                selection_plot = plot.get('selection', None)
                if selection_plot and selection:
                    plot_cp['selection'] = f"({selection_plot}) and ({selection})"
                else:
                    plot_cp['selection'] = selection_plot or selection
                df_chi2s.append(validation_plot(df_dt, df_mc, plot_cp, dir_out=dir, year=year))

            pd.concat(df_chi2s).to_csv(Path(dir) / 'chi2s_summary.csv')

    else:
        df_chi2s = []
        for plot in config_plot:
            if not plot.get('mll2', None) and add_mass:
                plot['mll2'] = add_mass
            if AN:
                df_chi2s.append(validation_plot_EGM(df_dt, df_mc, plot, dir_out=dir_out, year=year))
            else:
                df_chi2s.append(validation_plot(df_dt, df_mc, plot, dir_out=dir_out, year=year))

        pd.concat(df_chi2s).to_csv(Path(dir_out) / 'chi2s_summary.csv')


def ijazz_valid_plot_cmd():
    parser = argparse.ArgumentParser(description=f'IJazZ Validation plot tool')
    parser.add_argument('config_samples', type=str, help='yaml config file')
    parser.add_argument('--cfg', type=str, default=None, help='path to the yaml config with plots')
    parser.add_argument('--syst', action='store_true', help="add systematics")
    parser.add_argument('--AN', action='store_true', help="use AN mode, i.e. categories for lead only")
    parser.add_argument('--add_mass', type=str, default='', help='variables and name of a second mass to add to the plot, eg mass_egm:pt_egm:EGM')

    args = parser.parse_args(sys.argv[1:])
    AN = args.AN

    with open(args.config_samples, 'r') as fcfg:
        config = yaml.safe_load(fcfg)
    try: 
        with open(args.cfg, 'r') as fcfg:
            config_plot = yaml.safe_load(fcfg)['validation']
    except (FileNotFoundError, KeyError, TypeError):
        # plot config has not the right format, try directly the main config
        config_plot = config['validation']
    syst = args.syst
    ijazz_valid_plot(config, config_plot=config_plot, syst=syst, AN=AN, add_mass=args.add_mass)