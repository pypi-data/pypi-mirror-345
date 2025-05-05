import yaml
import pandas as pd
import numpy as np
from cms.common import var1d_reweighter, var2d_reweighter, bins_ptz_default, bins_rho_default, bins_eta_default
from pathlib import Path
from glob import glob
import uproot
import sys
from typing import List


column_lep = ["chargeEle", "etaSCEle", "R9Ele", "etaEle", "phiEle", "eleID", "gainSeedSC"]
column_evt = ["nPV", "rho", "runNumber", "eventNumber"]

weight_hist_dict = {
    '2016preVFP': {
        "Ele" : '/feynman/work/dphp/pg280968/repo/law_ijazz/analysis/configs/Run2/weight_hist/dataToMCweights_EGM_UL2016_preVFP_eleReg_noGenWeigt.root',
        "Pho" : '/feynman/work/dphp/pg280968/repo/law_ijazz/analysis/configs/Run2/weight_hist/dataToMCweights_EGM_UL2016_preVFP_phoReg_noGenWeigt.root'
    },
    '2016postVFP': {
        "Ele" : '/feynman/work/dphp/pg280968/repo/law_ijazz/analysis/configs/Run2/weight_hist/dataToMCweights_EGM_UL2016_postVFP_eleReg_noGenWeigt.root',
        "Pho" : '/feynman/work/dphp/pg280968/repo/law_ijazz/analysis/configs/Run2/weight_hist/dataToMCweights_EGM_UL2016_postVFP_phoReg_noGenWeigt.root'
    },
    '2017': {
        "Ele" : '/feynman/work/dphp/pg280968/repo/law_ijazz/analysis/configs/Run2/weight_hist/dataToMCweights_EGM_UL2017_eleReg_noGenWeigt.root',
        "Pho" : '/feynman/work/dphp/pg280968/repo/law_ijazz/analysis/configs/Run2/weight_hist/dataToMCweights_EGM_UL2017_phoReg_noGenWeigt.root'
    },
    '2018': {
        "Ele" : '/feynman/work/dphp/pg280968/repo/law_ijazz/analysis/configs/Run2/weight_hist/dataToMCweights_EGM_UL2018_eleReg_noGenWeigt.root',
        "Pho" : '/feynman/work/dphp/pg280968/repo/law_ijazz/analysis/configs/Run2/weight_hist/dataToMCweights_EGM_UL2018_phoReg_noGenWeigt.root'
    }
}


def main():
    help_msg = f"""Usage:
    reader_ecalelf config.yaml

    where the yaml config file contains the following fields:
    ------------------------------
    {read_and_convert.__doc__}
    """
    if len(sys.argv) != 2:
        print(help_msg)
        sys.exit(0)

    cfg = sys.argv[1]
    if cfg in ["--help", "-h"]:
        print(help_msg)
        sys.exit(0)

    print(f'HiggsDNA reader using config file: {cfg}')
    with open(cfg, 'r') as f_yaml:
        config = yaml.safe_load(f_yaml)['reader']
    read_and_convert(**config)


ele_id_fiduc = 1
ele_id_loose = int('0x0004', 16)
ele_id_tight = int('0x0010', 16)

def extract_from_root(file_list, is_mc, col_lep, col_evt, add_egm_sas=True, is_ele=False, selection=None):
    col_ener = "energy_ECAL_ele" if is_ele else "energy_ECAL_pho"
    col_scale = "energyScale_eleReg" if is_ele else "energyScale_phoReg" 
    #col_scale_err = "energyScaleWithErrUp_eleReg" if is_ele else "energyScaleWithErrUp_phoReg" 
    col_smear = "energySmear_eleReg" if is_ele else "energySmear_phoReg" 
    #col_smear_err = "energySmearWithErrUp_eleReg" if is_ele else "energySmearWithErrUp_phoReg" 
    extra_cols = ['Z_rapidity', 'Z_et', 'Z_energy', 'invMass_ECAL_ele', 'invMass_ECAL_pho']
    col_lep = col_lep + [col_ener]

    dfs = []
    for rfile_name in file_list:
        print(rfile_name)
        rfile = uproot.open(rfile_name)
        arrays = rfile['selected'].arrays(col_lep + col_evt)
        df = pd.DataFrame({k: arrays[k] for k in col_evt})

        leptons = col_lep
        if add_egm_sas:
            try:
                if is_mc:
                    print(' --> Add EGM MC with smearing')
                    # arr_smear = uproot.open(f'{rfile_name}_withSmear')['selected'].arrays([col_smear, col_scale, col_smear_err, col_scale_err]+ extra_cols)
                    # arr_smear = uproot.open(f'{rfile_name}_withSmear')['selected'].arrays([col_smear]+ extra_cols)
                    arr_smear = uproot.open(f'{rfile_name}_Refined')['selected'].arrays([col_smear]+ extra_cols)
                    # arr_smear = uproot.open(f'{rfile_name}_Standard')['selected'].arrays([col_smear]+ extra_cols)
                    arrays[f"{col_ener}_smear"] = arrays[col_ener] * arr_smear[col_smear]
                    # -- adding egm systematics
                    # arrays[f"{col_ener}_smear_up"] = arrays[col_ener] * arr_smear[col_smear_err]
                    # arrays[f"{col_ener}_scale_up"] = arrays[col_ener] * arr_smear[col_scale_err] / arr_smear[col_scale]
                    # leptons = leptons + [f"{col_ener}_smear", f"{col_ener}_smear_up", f"{col_ener}_scale_up"]
                    leptons = leptons + [f"{col_ener}_smear"]
                    for b in extra_cols:
                        df[b] = arr_smear[b]
                else:
                    print(' --> Add EGM Data with energy scale')
                    # arr_scale = uproot.open(f'{rfile_name}_withScale')['selected'].arrays([col_scale]+ extra_cols)
                    arr_scale = uproot.open(f'{rfile_name}_Refined')['selected'].arrays([col_scale]+ extra_cols)
                    # arr_scale = uproot.open(f'{rfile_name}_Standard')['selected'].arrays([col_scale]+ extra_cols)
                    # arrays[col_ener] = arrays[col_ener] * arr_scale[col_scale]
                    arrays[f"{col_ener}_scale"] = arrays[col_ener] * arr_scale[col_scale]
                    leptons = leptons + [f"{col_ener}_scale"]
                    for b in extra_cols:
                        df[b] = arr_scale[b]
            except FileNotFoundError:
                pass
        
        for b in leptons:
            for i_ele in [0, 1]:
                df[f'{b}{i_ele+1}'] = arrays[b][:, i_ele]

        for i_ele in [1, 2]:
            df[f'AbsScEta{i_ele}'] = df[f'etaSCEle{i_ele}'].abs()
            df[f"pt{i_ele}"] = df[f"{col_ener}{i_ele}"] / np.cosh(df[f"etaEle{i_ele}"])
            if f"{col_ener}_smear" in leptons:
                df[f"pt_egm{i_ele}"] = arrays[f"{col_ener}_smear"][:, i_ele-1] / np.cosh(df[f"etaEle{i_ele}"])
            if f"{col_ener}_scale" in leptons:
                df[f"pt_egm{i_ele}"] = arrays[f"{col_ener}_scale"][:, i_ele-1] / np.cosh(df[f"etaEle{i_ele}"])
            # -- adding egm systematics
            if f"{col_ener}_smear_up" in leptons:
                df[f"ptSmearUp{i_ele}"] = arrays[f"{col_ener}_smear_up"][:, i_ele-1] / np.cosh(df[f"etaEle{i_ele}"])
            if f"{col_ener}_scale_up" in leptons:
                df[f"ptScaleUp{i_ele}"] = arrays[f"{col_ener}_scale_up"][:, i_ele-1] / np.cosh(df[f"etaEle{i_ele}"])

        # df["passEleIDFiduc"] = ((arrays["eleID"][:, 0] & ele_id_fiduc) == ele_id_fiduc) & ((arrays["eleID"][:, 1] & ele_id_fiduc) == ele_id_fiduc)
        df["passEleIDLoose"] = ((arrays["eleID"][:, 0] & ele_id_loose) == ele_id_loose) & ((arrays["eleID"][:, 1] & ele_id_loose) == ele_id_loose)
        df["passEleIDTight"] = ((arrays["eleID"][:, 0] & ele_id_tight) == ele_id_tight) & ((arrays["eleID"][:, 1] & ele_id_tight) == ele_id_tight)

        df["mass"] = df.eval("sqrt(2*pt1*pt2*(cosh(etaEle1-etaEle2)-cos(phiEle1-phiEle2)))")
        if f"{col_ener}_smear" in leptons:
            df["mass_egm"] = df.eval("sqrt(2*pt_egm1*pt_egm2*(cosh(etaEle1-etaEle2)-cos(phiEle1-phiEle2)))")
        elif f"{col_ener}_scale" in leptons:
            df["mass_egm"] = df.eval("sqrt(2*pt_egm1*pt_egm2*(cosh(etaEle1-etaEle2)-cos(phiEle1-phiEle2)))")
        else:
            df["mass_egm"] = df['mass']
        
        # -- adding egm systematics
        if f"{col_ener}_smear_up" in leptons:
            df["mass_egm_smear_up"] = df.eval("sqrt(2*ptSmearUp1*ptSmearUp2*(cosh(etaEle1-etaEle2)-cos(phiEle1-phiEle2)))")
        if f"{col_ener}_scale_up" in leptons:
            df["mass_egm_scale_up"] = df.eval("sqrt(2*ptScaleUp1*ptScaleUp2*(cosh(etaEle1-etaEle2)-cos(phiEle1-phiEle2)))")

        df["ptz"] = df.eval("sqrt(pt1**2 + pt2**2 + 2*pt1*pt2*cos(phiEle1-phiEle2))")
        df["y_z"] = df.eval(f"0.5 * log(({col_ener}1 + {col_ener}2 + pt1 * sinh(etaEle1) + pt2 * sinh(etaEle2)) / ({col_ener}1 + {col_ener}2 - pt1 * sinh(etaEle1) - pt2 * sinh(etaEle2)))")
        
        print(f"Apply SELECTION: {selection}")
        if selection is not None:
            df = df.query(selection)
        dfs.append(df)
    return pd.concat(dfs)


# -- reading and preparing data
def read_and_convert(dir_dt:str=None, dir_mc:str=None, dir_out:str=None, stem_out:str=None, is_ele=False, mc_weight:str ='weight', year:str=None,
                     corrlib_scale:dict=None, corrlib_smear:dict=None, add_vars:List=None, reweight_selection:str=None, add_egm_sas:bool=True, reweight_Badder:bool=True):
    """Read and convert the higgsDNA parquet file to the ijazz_2p0 format
    Args (can be set with a config file):
        dir_dt (str, optional): Directory with data files (can be a file). Defaults to None.
        dir_mc (str, optional):  Directory with data files (can be a file). Defaults to None.
        dir_out (str, optional): Output directory. Defaults to None.
        stem_out (str, optional): Stem of the output file (it will be completed with different option). Defaults to None.
        is_ele (bool, optional): Use the GSF electron energy. Defaults to False.
        mc_weight (str, optional): name of the column containing the MC weights. Defaults to 'weight'.
        corrlib_scale (dict, optional): correction lib to correct the energy scale in data. Defaults to None.
        corrlib_smear (dict, optional): correction lib to smear the MC. Defaults to None.
        add_egm_sas (bool, optional): Add the EGM scale and smear. Defaults to True.
        add_vars (List, optional): List of additional variables to add to the output. Defaults to None.

    Raises:
        AttributeError: dir_out has to be set
        AttributeError: stem_out has to be set
        AttributeError: dir_dt or dir_mc has to be set
    """

    if dir_out is None:
        raise AttributeError(f'config file has no attribute dir_out')
    else:
        dir_out = Path(dir_out)
    if stem_out is None:
        raise AttributeError(f'config file has no attribute stem_out')

    columns = column_evt

    if mc_weight is not None:
        columns  += [mc_weight]
    
    if add_vars is not None:
        columns += add_vars

    selection = 'chargeEle1*chargeEle2 < 0 and passEleIDLoose'
    selection += ' and abs(Z_rapidity) < 2.5'
    selection += ' and ((AbsScEta1 < 1.4442) or (AbsScEta1 > 1.566)) and ((AbsScEta2 < 1.4442) or (AbsScEta2 > 1.566))'
    selection += ' and AbsScEta1 < 2.5 and AbsScEta2 < 2.5 & pt1 > 23 & pt2 > 20 and mass < 120' 
    dt = None

    if dir_dt is not None:
        dt_files = dir_dt if Path(dir_dt).is_file() else glob(f'{dir_dt}', recursive=True)
        dt = extract_from_root(dt_files, is_ele=is_ele, col_lep=column_lep, selection=selection, col_evt=columns, is_mc=False, add_egm_sas=add_egm_sas)

    mc = None
    if dir_mc is not None:
        mc_files = dir_mc if Path(dir_mc).is_file() else glob(f'{dir_mc}', recursive=True)
        mc = extract_from_root(mc_files, is_ele=is_ele, col_lep=column_lep, selection=selection, col_evt=columns + ["mcGenWeight"], is_mc=True, add_egm_sas=add_egm_sas)
    
                
    if mc is not None and dt is not None:
        print('Compute reweightings (ZPT, rho, eta 2D...)')
        print(reweight_selection if reweight_selection else '80 < mass < 100')
        # apply the reweighting to all MC events but compute it in the Z mass window
        mask_dt = dt.eval(reweight_selection if reweight_selection else '80 < mass < 100')
        mask_mc = mc.eval(reweight_selection if reweight_selection else '80 < mass < 100')

        # -- zpt reweighting
        if mc_weight is None:
            mc_weight = 'weight'
            mc[mc_weight] = 1
        mc['weight_z_pt'] = var1d_reweighter(dt.loc[mask_dt, 'ptz'], mc['ptz'], mc[mc_weight], 
                                             bins_var=bins_ptz_default, mc_mask=mask_mc)

        mc[mc_weight] *= mc['weight_z_pt']

        mc['weight_rho'] = var1d_reweighter(dt.loc[mask_dt, 'rho'], mc['rho'], mc[mc_weight], 
                                            bins_var=bins_rho_default, mc_mask=mask_mc)
        mc[mc_weight] *= mc['weight_rho']

        mc['weight_eta'] = var2d_reweighter(dt.loc[mask_dt, 'etaSCEle1'], dt.loc[mask_dt, 'etaSCEle2'], 
                                            mc['etaSCEle1'], mc['etaSCEle2'],
                                            bins_2d_var=(bins_eta_default, bins_eta_default),
                                            mc_weights=mc[mc_weight], mc_mask=mask_mc)
        mc[f'{mc_weight}_no_eta'] = mc[mc_weight]
        mc[mc_weight] *= mc['weight_eta']

        #-- NLO reweighting
        mc['weight_z_pt_gen'] = var1d_reweighter(dt.loc[mask_dt,'ptz'], mc['ptz'], mc['mcGenWeight'], 
                                                bins_var=bins_ptz_default, mc_mask=mask_mc)
        mc['weight_gen'] = mc['mcGenWeight'] *  mc['weight_z_pt_gen']
        mc['weight_gen'] *= mc['weight_rho']
        mc['weight_gen'] *= mc['weight_eta']

        # -- normalize the MC to the xsec
        norm_factor = dt.shape[0] / mc[mc_weight].sum()
        print(f'Normalize MC with norm factor {norm_factor:.3g}')
        mc[mc_weight] *= norm_factor
        mc['weight_gen'] *= dt.shape[0] / mc['weight_gen'].sum()
    
    elif mc is not None:
        print('I will not reweight the ZpT in the simulation because no data are set')

    if mc is not None and reweight_Badder:
        print('Saving the reweighting from Badder')
        reweight_hist = weight_hist_dict[year]["Ele"] if is_ele else weight_hist_dict[year]["Pho"]
        file = uproot.open(reweight_hist)
        #loading histograms
        nPV_weight, nPV_bins = file['h_nPV_total_weights'].to_numpy()
        Z_pt_absY_weight, Z_pt_bins, absY_bins = file['h2_Z_pt-absY_total_weights'].to_numpy()

        # Find bin indices for each event
        Z_pt_idx = np.digitize(mc["Z_et"], Z_pt_bins) - 1
        absY_idx = np.digitize(mc["Z_rapidity"].abs(), absY_bins) - 1
        nPV_idx = np.digitize(mc["nPV"].abs(), nPV_bins) - 1

        # Ensure indices are within valid range
        Z_pt_idx = np.clip(Z_pt_idx, 0, len(Z_pt_bins) - 2)
        absY_idx = np.clip(absY_idx, 0, len(absY_bins) - 2)
        nPV_idx = np.clip(nPV_idx, 0, len(nPV_bins) - 2)

        mc["weightMin"] = Z_pt_absY_weight[Z_pt_idx, absY_idx] * nPV_weight[nPV_idx]


    
    # -- saving the parquet file
    stem_out += ".ele" if is_ele else ".pho"    
    dir_out.mkdir(parents=True, exist_ok=True)
    if dt is not None:
        print(f'Saving {dir_out / stem_out}.data.parquet')
        dt.to_parquet(dir_out / f"{stem_out}.data.parquet", engine="auto")
    if mc is not None:
        print(f'Saving {dir_out / stem_out}.mc.parquet')
        mc.to_parquet(dir_out / f"{stem_out}.mc.parquet", engine="auto")


if __name__ == "__main__":
    main()
