import numpy as np
import pandas as pd
from typing import Tuple, Union, List, Dict
import correctionlib
from pathlib import Path
from scipy.stats import binned_statistic_2d
import argparse
import yaml
import sys
from glob import glob


bins_ptz_default = np.concatenate([np.linspace(0,100, 101)[:-1], np.linspace(100, 300, 41)]) 
bins_rho_default = np.linspace(-0.5, 60.5, 31)
bins_eta_default = np.linspace(-2.5, 2.5, 26)
cast_type = np.float32


def var1d_reweighter(var_dt: np.ndarray, var_mc: np.ndarray, mc_weights:np.ndarray=None, 
                     bins_var:np.ndarray=bins_ptz_default, mc_mask=None) -> np.ndarray:
    """Function to reweight the di-lepton pT in MC to the one in data

    Args:
        var_dt (np.ndarray): data pT_ll
        var_mc (np.ndarray): MC pT_ll
        mc_weights (np.ndarray, optional): MC weights. Defaults to None.
        mc_mask (np.ndarray): Mask to be applied on MC when computing the MC histogram for reweight.
        bins_var (np.ndarray, optional): binning used for di-lepton pT reweights. Defaults to np.concatenate([np.linspace(0,100, 101)[:-1], np.linspace(100, 300, 41)]).

    Returns:
        np.ndarray: list of weights per MC event
    """
    if mc_mask is None:
        mc_mask = slice(0, None)

    mc_w = None if mc_weights is None else mc_weights[mc_mask]
    xr = (bins_var[0], bins_var[-1])
    h_var_dt, x_var = np.histogram(var_dt.clip(*xr), bins=bins_var)
    h_var_mc, x_var = np.histogram(var_mc[mc_mask].clip(*xr), bins=bins_var, weights=mc_w)

    h_var_dt = h_var_dt.astype(np.float64)
    h_var_mc = h_var_mc.astype(np.float64)
    x_width = (x_var[1:] - x_var[:-1])
    h_var_dt /= x_width
    h_var_mc /= x_width
    h_var_mc *= h_var_dt.sum() / h_var_mc.sum()

    w_var = h_var_dt / h_var_mc
    ibin = np.digitize(var_mc, bins_var) - 1
    weights = w_var[np.where(ibin >= len(w_var), len(w_var)-1, ibin)]
    return weights


def var2d_reweighter(var_dt_x: np.ndarray, var_dt_y: np.ndarray,
                     var_mc_x: np.ndarray, var_mc_y: np.ndarray,
                     bins_2d_var:Tuple[np.ndarray, np.ndarray]=(bins_eta_default, bins_eta_default),
                     mc_weights:np.ndarray=None, mc_mask=None) -> np.ndarray:
    """Generate a 2D reweighting

    Args:
        var_dt_x (np.ndarray): data X 
        var_dt_y (np.ndarray): data Y
        var_mc_x (np.ndarray): MC X
        var_mc_y (np.ndarray): MC Y
        mc_mask (np.ndarray): Mask to be applied on MC when computing the MC 2D histogram
        bins_2d_var (Tuple[np.ndarray, np.ndarray], optional): 2D bining. Defaults to (bins_eta_default, bins_eta_default).
        mc_weights (np.ndarray, optional): MC weights. Defaults to None.

    Returns:
        np.ndarray: return the weight associated to each events
    """
    if mc_mask is None:
        mc_mask = slice(0, None)

    mc_w = None if mc_weights is None else mc_weights[mc_mask]

    xr = (bins_2d_var[0][0], bins_2d_var[0][-1])
    yr = (bins_2d_var[1][0], bins_2d_var[1][-1])
    h_dt, _, _ = np.histogram2d(var_dt_x.clip(*xr), var_dt_y.clip(*yr), bins=bins_2d_var)
    h_mc, _, _ = np.histogram2d(var_mc_x[mc_mask].clip(*xr), var_mc_y[mc_mask].clip(*yr),
                                bins=bins_2d_var, weights=mc_w)                          

    # do not care about the histogram, just the digitizing
    _, _, _, bin_mc = binned_statistic_2d(var_mc_x.clip(*xr), var_mc_y.clip(*yr),
                                          None, 'count',                                             
                                          expand_binnumbers=True, bins=bins_2d_var)
                                             
    w_2d = h_dt / h_mc * (h_mc.sum() / h_dt.sum())
    w = w_2d[bin_mc[0]-1, bin_mc[1]-1]
    w = np.where(np.isnan(w) | np.isinf(w), 1 ,w)
    return w


def fig_add_text(figs:List, iax:int, text:Union[List, str], dx=0.05, dy=0.90, fs=12, scale=1, year:Union[int, str]=None, x_pos=None):
    """Add text on a list of figure

    Args:
        figs (List): list of figures
        iax (int): axis number in the aces from the figure
        text (str): text to be added
        x_pos (int, optional): absolue x position . Defaults to 81.
        dy (float, optional): relative y position. Defaults to 0.90.
        fs (int, optional): fontsize. Defaults to 12.
        scale (int, optional): scale the y range. Defaults to 1.
        x_pos_relative(bool, optional): use a relative x position. Default to False
        year (Union[int, str], optional): year name. Defaults to None.
    """
    if isinstance(text, str):
        texts = [text]*len(figs)
    else:
        texts = text
    for fig, text in zip(figs, texts):
        ax = fig.get_axes()[iax]
        if year is not None:
            ax.set_title(year, loc='right')
        y0, y1 = ax.get_ylim()
        y1 = y1*scale
        ax.set_ylim(y0, y1)
        dy = dy * scale
        if x_pos:
            x0, x1 = ax.get_xlim()
            dx = (x_pos - x0)/(x1-x0)
        ax.text(dx, dy, text, fontsize=fs, transform=ax.transAxes)

def double_smearing(std_normal, std_flat, mu, sigma1, sigma2, frac):
    # Compute the two possible scale values 
    scale1 = 1 + sigma1 * std_normal
    scale2 = mu * (1 + sigma2 * std_normal)
    
    # Compute binomial selection
    binom = std_flat > frac
 
    return np.where(binom, scale2, scale1)


def read_and_correct_parquet(afile:Union[str, Path, pd.DataFrame], corrlib:Union[str, Path]=None, 
                             cset_name:str=None, cset_vars:List[str]=None, mll_name='mass',
                             second_cset_name:str=None, second_cset_vars:List[str]=None, 
                             syst_name='scale',syst_names: dict=None,
                             is_second_cset_egm:bool=False,
                             double_gaussian=False, columns=None) -> pd.DataFrame:
    
    """
    Reads a Parquet file or DataFrame, applies corrections and systematic variations, 
    and returns the corrected DataFrame.
    Args:
        afile (Union[str, Path, pd.DataFrame]): Input file path (str or Path) or a pandas DataFrame.
        corrlib (Union[str, Path], optional): Path to the correction library file. If provided, 
            corrections will be applied. Defaults to None.
        cset_name (str, optional): Name of the correction set to use. If not provided, it will be 
            extracted from `corrlib`. Defaults to None.
        cset_vars (List[str], optional): List of variable names required for the correction set. 
            Defaults to None.
        mll_name (str, optional): Name of the invariant mass column. Defaults to 'mass'.
        second_cset_name (str, optional): Name of the second correction set for additional corrections. 
            Defaults to None.
        second_cset_vars (List[str], optional): List of variable names required for the second correction set. 
            Defaults to None.
        syst_name (str, optional): Name of the systematic variation to apply. Options include 'scale', 
            'scale_up', 'scale_down', 'smear', 'smear_up', 'smear_down'. Defaults to 'scale'.
        syst_names (dict, optional): Dictionary mapping systematic names to their respective nominal 
            and error keys. Defaults to None.
        is_second_cset_egm (bool, optional): Whether the second correction set is for energy scale corrections. 
            Defaults to False.
        double_gaussian (bool, optional): Whether to use double Gaussian smearing for systematic variations. 
            Defaults to False.
        columns (list, optional): List of columns to read from the Parquet file. Defaults to None.
    Returns:
        pd.DataFrame: The corrected DataFrame with systematic variations applied.
    Raises:
        IndexError: If `syst_name` is not in the list of available systematic variations.
        TypeError: If an unknown systematic type is provided in `syst_name`.
    Notes:
        - The function supports both scale and smearing corrections.
        - If `corrlib` is provided, the correction library is loaded, and corrections are applied 
            based on the specified correction sets and variables.
        - Systematic variations can be applied by specifying `syst_name`.
        - Double Gaussian smearing can be enabled for more complex systematic variations.
    """

    df: pd.DataFrame = afile if isinstance(afile, pd.DataFrame) else pd.read_parquet(afile, columns=columns) 
    use_scale_correction = False

    if corrlib:
        if cset_name is None:
            corrlib, cset_name = corrlib.split(':')
        cset = correctionlib.CorrectionSet.from_file(corrlib)
        try:
            corr = cset[cset_name]
        except IndexError:
            corr = cset.compound[cset_name]

        random_corr = None
        if second_cset_name is not None:
            if is_second_cset_egm:
                corr2 = cset[second_cset_name]
                use_scale_correction = True
                print('Using scale correction')
            else:
                random_corr = cset[second_cset_name]

        if syst_names is None:
            syst_names = {
                'scale': {'nominal': 'scale', 
                          'err' : 'escale'},
                'smear': {'nominal': 'smear', 
                          'err' : 'esmear',
                         },
                'reso2': {'nominal': 'reso2'},
                'mu': {'nominal': 'mu'},
                'frac': {'nominal': 'frac'},
            }
        
        available_syst = [None, 'scale', 'scale_up', 'scale_down', 'smear', 'smear_up', 'smear_down']
        if not syst_name in available_syst:
            raise IndexError(f'syst_name {syst_name} is not in {available_syst}')

        is_smear = True if syst_name in ['smear', 'smear_up', 'smear_down'] else False
        is_syst = True if syst_name in ['scale_up', 'scale_down', 'smear_up', 'smear_down'] else False

        ele_names = [f'{name}1' for name in cset_vars]
        ele_names = [name.split('1')[0] for name in df.columns.intersection(ele_names)]
 
        if second_cset_name is not None:
            ele_second_names = [f'{name}1' for name in second_cset_vars]
            ele_second_names = [name.split('1')[0] for name in df.columns.intersection(ele_second_names)]

        if not is_syst:
            df[f'{mll_name}_raw'] = df[mll_name]
        for i_ele in [1, 2]:
            if not is_syst:
                df[f'pt_raw{i_ele}'] = df[f'pt{i_ele}']
            ele_vars = [df[f'{var}{i_ele}' if var in ele_names else var] for var in cset_vars]
        
            if second_cset_name is not None:
                ele_second_vars = [df[f'{var}{i_ele}' if var in ele_second_names else var] for var in second_cset_vars]
                
            
            if is_syst:
                sign_syst = +1. if "up" in syst_name else -1.
                if "scale" in syst_name:
                    # -- escale is already a relative error
                    if use_scale_correction:
                        scales = 1 + sign_syst*corr2.evaluate(*([syst_names['scale']['err']] + ele_second_vars))
                    else:
                        scales = 1 + sign_syst*corr.evaluate(*([syst_names['scale']['err']] + ele_vars))
                    # -- add nominal smearing
                    smears = corr.evaluate(*([syst_names['smear']['nominal']] + ele_vars))
                    if double_gaussian:
                        print('Using double gaussian smearing')
                        scales *= double_smearing(random_corr.evaluate(*(['stdnormal'] + ele_second_vars)), 
                                                  random_corr.evaluate(*(['stdflat'] + ele_second_vars)), 
                                                  corr.evaluate(*([syst_names['mu']['nominal']] + ele_vars)),
                                                  smears,
                                                  corr.evaluate(*([syst_names['reso2']['nominal']] + ele_vars)),
                                                  corr.evaluate(*([syst_names['frac']['nominal']] + ele_vars))
                                                  )
                    else:
                        try :
                            scales *= 1 + smears * random_corr.evaluate(*(['stdnormal'] + ele_second_vars))
                            print('Smearing using the included random number generator')
                        except (IndexError, KeyError, AttributeError):
                            scales *= np.random.normal(1, smears)
                            print('Smearing using numpy random')
                elif "smear" in syst_name:
                    scales = corr.evaluate(*([syst_names['smear']['nominal']] + ele_vars)) + sign_syst*corr.evaluate(*([syst_names['smear']['err']] + ele_vars))
                else:
                    raise TypeError(f"Unknown systematic type {syst_name}")
            else: 
                eval_args = ele_vars if syst_name is None else [syst_names[syst_name]['nominal']] + ele_vars
                scales = corr.evaluate(*eval_args)

            if is_smear:   # --  for smearing randomize the scale
                if double_gaussian:
                    print('Using double gaussian smearing')
                    scales = double_smearing(random_corr.evaluate(*(['stdnormal'] + ele_second_vars)), 
                                             random_corr.evaluate(*(['stdflat'] + ele_second_vars)), 
                                             corr.evaluate(*([syst_names['mu']['nominal']] + ele_vars)),
                                             scales,
                                             corr.evaluate(*([syst_names['reso2']['nominal']] + ele_vars)),
                                             corr.evaluate(*([syst_names['frac']['nominal']] + ele_vars))
                                             )
                else:
                    try:
                        scales *= random_corr.evaluate(*(['stdnormal'] + ele_second_vars))
                        scales += 1.0
                        print('Smearing using the included random number generator')
                    except (IndexError, KeyError, UnboundLocalError, AttributeError):
                        scales = np.random.normal(1, scales)
                        print('Smearing using numpy random')

            if is_syst:
                df[f'pt_{syst_name}{i_ele}'] = (df[f'pt{i_ele}'] * scales).astype(cast_type)
                if i_ele == 1:
                    df[f'{mll_name}_{syst_name}'] = (df[mll_name] * np.sqrt(scales)).astype(cast_type)
                else:
                    df[f'{mll_name}_{syst_name}'] = (df[f'{mll_name}_{syst_name}'] * np.sqrt(scales)).astype(cast_type)
            else:
                df[f'pt{i_ele}'] = (df[f'pt{i_ele}'] * scales).astype(cast_type)
                df[mll_name] = (df[mll_name] * np.sqrt(scales)).astype(cast_type)

                # if is_smear:
                #     df[f'ptSmearing{i_ele}'] = scales
                #     df[f'smear{i_ele}'] = corr.evaluate(*[syst_names['smear']['nominal']] + ele_vars)
                #     df[f'esmear{i_ele}'] = corr.evaluate(*[syst_names['smear']['err']] + ele_vars)
                #     df[f'escale{i_ele}'] = corr.evaluate(*[syst_names['scale']['err']] + ele_vars)
                # else:
                #     df[f'ptScale{i_ele}'] = scales
                #     df[f'escale{i_ele}'] = corr.evaluate(*[syst_names['scale']['err']] + ele_vars)
    
    return df


def get_df_with_correction(config_files:List[Dict], mll_name='mee', is_mc=False, do_syst=False, egm=False, merge_files=True) -> pd.DataFrame:
    """Load the data and apply the correction to the mass and pt`

    Args:
        config_files (List[Dict]): list of files from config files, each file should contain 
                                {'name': file_name, 'corrlib': {'path': path_to_corr, 'cset_name': cset name in corrlib file, 'cset_vars': [x1, x2, x3]}}
        mll_name (str, optional): di-lepton mass. Defaults to 'mee'.
        is_mc (bool, optional): if True, the file is a MC file, eg we can apply syst to its. Defaults to False.
        do_syst (bool, optional): add systematic variations. Defaults to False.
        egm (bool, optional): if True, the second correction set is for EGM because the scale and smearing systematics are in two different cset. Defaults to False.
        merge_files (bool, optional): if True, merge the files. Defaults to True.

    Returns:
        pd.DataFrame: dataframe with the dy data and the correction applied to the mass and pts
    """
    dfs = []
    for afile in config_files:
        file_name = afile['path']
        nfiles = afile.get('nfiles', -1)
        file_name = file_name if Path(file_name).is_file() else glob(f'{file_name}/*.parquet', recursive=True)
        if not Path(afile['path']).is_file():
            file_name = file_name[:nfiles]
        corrlib = afile.get('corrlib', None)
        clib_path, cset_name, cset_vars, second_cset_name, second_cset_vars, syst_names, double_gaussian = (None, None, None, None, None, None, None)
        

        if corrlib:
            print(f' - file: {file_name}')
            clib_path = corrlib['path']
            cset_name = corrlib['cset_name']
            cset_vars = corrlib['cset_vars']
            syst_names = corrlib.get('syst_names', None)
            double_gaussian = corrlib.get('double_gaussian', False)
        
            second_cset_name = corrlib.get('random_cset_name', None)
            second_cset_vars = corrlib.get('random_cset_vars', None)
            if egm:
                second_cset_name = corrlib['cset_name2']
                second_cset_vars = corrlib['cset_vars2']
        
        dfs.append(read_and_correct_parquet(file_name))
        if do_syst and is_mc:
            # -- S&S syst must be done prior to nominal smearing
            print('  - adding "smear_up"')
            read_and_correct_parquet(dfs[-1],  mll_name=mll_name, syst_name='smear_up', 
                                     corrlib=clib_path, cset_vars=cset_vars, cset_name=cset_name,
                                     syst_names=syst_names, double_gaussian=double_gaussian,
                                     second_cset_name=second_cset_name, second_cset_vars=second_cset_vars, is_second_cset_egm=egm)
            print('  - adding "scale_up"')
            read_and_correct_parquet(dfs[-1],  mll_name=mll_name, syst_name='scale_up', 
                                     corrlib=clib_path, cset_vars=cset_vars, cset_name=cset_name,
                                     syst_names=syst_names, double_gaussian=double_gaussian,
                                     second_cset_name=second_cset_name, second_cset_vars=second_cset_vars, is_second_cset_egm=egm)
        if corrlib:
            # -- apply nominal S&S
            print('  - nominal correction')
            syst_name = 'smear' if is_mc else 'scale'
        
            read_and_correct_parquet(dfs[-1],  mll_name=mll_name, syst_name=syst_name,
                                     corrlib=clib_path, cset_vars=cset_vars, cset_name=cset_name,syst_names=syst_names, 
                                     double_gaussian=double_gaussian, second_cset_name=second_cset_name, second_cset_vars=second_cset_vars)


    return dfs[0] if len(dfs) == 1 else pd.concat(dfs).reset_index(drop=True) if merge_files else dfs


def ijazz_file_corrector():
    parser = argparse.ArgumentParser(description=f'IJazZ file corrector tool')
    parser.add_argument('config_samples', type=str, help='yaml config file')
    parser.add_argument('--syst', action='store_true', help="add systematics")
    parser.add_argument('--egm', action='store_true', help="add systematics")
    args = parser.parse_args(sys.argv[1:])
    with open(args.config_samples, 'r') as fcfg:
        config = yaml.safe_load(fcfg)
    syst = args.syst
    file_corrector(config, syst, args.egm)

def file_corrector(config: Dict=None, syst :bool=False, egm: bool=False):
    mll_name = config.get('mll_name', 'mee')

    print('Apply correction to data files')
    df_dt = get_df_with_correction(config['file_dt'], mll_name=mll_name, is_mc=False, do_syst=False)
    print('Apply correction to MC files')
    df_mc = get_df_with_correction(config['file_mc'], mll_name=mll_name, is_mc=True, do_syst=syst, egm=egm)
    print(f"  --> saving corrected ijazz data file to: {config.get('file_dt_out', None)}")    
    df_dt.to_parquet(config.get('file_dt_out', None))
    print(f"  --> saving corrected ijazz mc file to: {config.get('file_mc_out', None)}")
    df_mc.to_parquet(config.get('file_mc_out', None))


def get_file_name(file_name, cfg_reader, is_mc):
    # infer name from the reader config
    if file_name is None:
        stem_out = cfg_reader['stem_out']
        stem_out += ".ele" if cfg_reader.get('is_ele', False) else ".pho"
        stem_out += '.mc' if is_mc else '.data'
        file_name = Path(cfg_reader['dir_out']) / f'{stem_out}.parquet'
    return Path(file_name)