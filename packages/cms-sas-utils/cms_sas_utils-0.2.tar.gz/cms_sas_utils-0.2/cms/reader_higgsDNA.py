import yaml
import pandas as pd
import numpy as np
from cms.common import var1d_reweighter, var2d_reweighter, bins_ptz_default, bins_eta_default
from pathlib import Path
from glob import glob
import correctionlib
import sys
from typing import List
import pyarrow.parquet as pq
from tqdm import tqdm

# -- normalisation for bkg study

# normalisation = {'XS': {'DY': 6688.0, 'WJets_0J': 55760, 'WJets_1J': 9529, 'WJets_2J': 3532, 'TTto2L2Nu': 762.1 }, 'Lumi':{'2023preBPIX': 17794, '2023postBPIX': 9451}}
# normalisation = {'XS': {'DY': 5467.0, 'WJets_0J': 55760, 'WJets_1J': 9529, 'WJets_2J': 3532, 'TTto2L2Nu': 923.6 }, 'Lumi':{'2023preBPIX': 17794, '2023postBPIX': 9451, '2024': 108960}}
# normalisation = {'XS': {'DY': 6688.0, 'WJets_0J': 55760, 'WJets_1J': 9529, 'WJets_2J': 3532, 'TTto2L2Nu': 923.6 }, 'Lumi':{'2023preBPIX': 17794, '2023postBPIX': 9451, '2024': 108960}}
normalisation = {'XS': {'DYto2L': 6688.0, 'DYto2E': 6688.0/3, 'DYto2Tau': 6688.0/3, 'WJets_0J': 55760, 'WJets_1J': 9529, 'WJets_2J': 3532, 'TTto2L2Nu': 95.49 }, 'Lumi':{'2023preBPIX': 17794, '2023postBPIX': 9451, '2024': 108960}}
# normalisation = {'XS': {'DY': 6688.0, 'WJets_0J': 55760, 'WJets_1J': 9529, 'WJets_2J': 3532, 'TTto2L2Nu': 923.6 }, 'Lumi':{'2023preBPIX': 17794, '2023postBPIX': 9451, '2024': 15200}}

# -- columns for photons
columns_pho = ["mass", "pt", "lead_pt", "lead_r9", "lead_ScEta", "lead_phi", "lead_eta", "lead_mvaID",
               "sublead_pt", "sublead_r9", "sublead_ScEta", "sublead_phi", "sublead_eta", "sublead_mvaID",]
columns_pho = ["mass", "pt", "lead_pt", "lead_r9", "lead_ScEta", "lead_phi", "lead_eta", "lead_mvaID",
               "sublead_pt", "sublead_r9", "sublead_ScEta", "sublead_phi", "sublead_eta", "sublead_mvaID",
               "lead_PassPresel", "sublead_PassPresel", "lead_seedGain", "sublead_seedGain",
               "lead_isScEtaEB", "lead_isScEtaEE", "sublead_isScEtaEB", "sublead_isScEtaEE", 
            #    'sublead_seediEtaOriX', 'sublead_seediPhiOriY', 'lead_seediEtaOriX', 'lead_seediPhiOriY',
               "run", "event", 'nPV', 'fixedGridRhoAll']


# -- columns to add for electrons
columns_ele = ["lead_ele_pt", "sublead_ele_pt"]

# -- filters
filters_pho = [("lead_pt", ">", 23), ("sublead_pt", ">", 12)]
filters_ele = [("lead_ele_pt", ">", 23), ("sublead_ele_pt", ">", 12)]
filters_evt = [
    ("mass", ">", 65), ("mass", "<", 115),
    # ("lead_mvaID", ">", -0.9), ("sublead_mvaID", ">", -0.9)
    # ("lead_ele_cutBased", ">", 0), ("sublead_ele_cutBased", ">", 0)
    ]
filters_pho += filters_evt
filters_ele += filters_evt


def main():
    help_msg = f"""Usage:
    reader_higgsdna config.yaml

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


# -- reading and preparing data
def read_and_convert(data_dict:dict=None, mc_dict:dict=None, dir_out:str=None, stem_out:str=None, is_ele=False,
                     corrlib_scale:dict=None, corrlib_smear:dict=None, remove_HDNA_SaS:bool=False, add_vars:List=None, charge:int=-1, 
                     selection:str=None, do_normalisation:bool=False, reweight_selection:str=None, pileup_reweighting:bool=False, do_reweight:bool=True,
                     subyear:str=None, subyear_list:list=None, backgrounds:list=[], year:str='', save_dt:bool=True, save_mc:bool=True):
    """Read and convert the higgsDNA parquet file to the ijazz_2p0 format. 
    Args (can be set with a config file):
        data_dict (dict): dictionary with the data information:
            - dir (str): directory of the data parquet files
            - luminosity (float): luminosity of the data taking (optionnal)
        mc_dict (dict): dictionary with the MC information:
            - dir (str): directory of the MC parquet files
            - name (str): name of the MC sample (optionnal)
            - XS (float): cross section of the MC sample (optionnal)
        dir_out (str, optional): Output directory. Defaults to None.
        stem_out (str, optional): Stem of the output file (it will be completed with different option). Defaults to None.
        is_ele (bool, optional): Use the GSF electron energy. Defaults to False.
        corrlib_scale (dict, optional): correction lib to correct the energy scale in data. Defaults to None.
        corrlib_smear (dict, optional): correction lib to smear the MC. Defaults to None.
        add_vars (List, optional): List of additional variables to add. Defaults to None.
        charge (int, optional): Charge selection: -1 for opposite charge, 1 for same charge and 0 for no selection. Defaults to -1.
        selection (str, optional): Additional selection to apply. Defaults to None.
        do_normalisation (bool, optional): Apply the normalisation. Defaults to False.
        reweight_selection (str, optional): Selection to apply to compute the reweighting. Defaults to None.
        pileup_reweighting (bool, optional): Apply the pileup reweighting. Defaults to False.
        do_reweight (bool, optional): Apply the reweighting. Defaults to True.
        subyear (str, optional): Subyear to add to the data. Used for luminosity (if not provided) and to add a tag `is_{subyear}` on the subyear samples. Defaults to None.
        subyear_list (list, optional): List of subyears tags to add. Defaults to None.
        backgrounds (list, optional): List of background dict. Defaults to []. Each dict should contain:
            - name (str): name of the background
            - dir (str): directory of the background parquet files
            - XS (float): cross section of the background sample (optionnal)
        year (str, optional): Year of the data taking. Defaults to ''.
        save_dt (bool, optional): Save the data. Defaults to True.
        save_mc (bool, optional): Save the MC. Defaults to True.


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

    filters = filters_ele if is_ele else filters_pho
    columns = columns_pho 
    if is_ele:
        columns += columns_ele
    if add_vars is not None:
        columns += add_vars
    if charge:
        columns += ["lead_ele_charge", "sublead_ele_charge"]
    if remove_HDNA_SaS:
        columns += ["lead_pt_raw", "sublead_pt_raw"]

    # -- read files
    columns_dt = columns
    columns_mc = columns + ["genWeight", "weight_central", "weight"]
    
    dt_files = None
    dir_dt = data_dict.get('dir', None)
    if dir_dt is not None:
        dt_files = dir_dt if Path(dir_dt).is_file() else glob(f'{dir_dt}/*.parquet', recursive=True)
    mc_files = None
    dir_mc = mc_dict.get('dir', None)
    if dir_mc is not None:
        mc_files = dir_mc if Path(dir_mc).is_file() else glob(f'{dir_mc}/*.parquet', recursive=True)
    
    do_normalisation = do_normalisation or backgrounds != []
    if do_normalisation:
        # -- read the sum_genw_presel and load the backgrounds
        sum_genw_presel_bkg = []
        bkgs = []
        bkg_files = {}
        for i,bkg in enumerate(backgrounds):
            if (bkg['name'] not in ['WJets_0J', 'WJets_1J', 'WJets_2J', 'TTto2L2Nu', 'DYto2Tau']) and 'XS' not in bkg:
                raise ValueError(f'Background {bkg} not supported. Please provide the cross section in the config file')
            elif 'dir' not in bkg:
                raise ValueError(f'Please provide the directory of background {bkg} in the config file')
            else:
                bkg_files[bkg['name']] = [bkg["dir"]] if Path(bkg["dir"]).is_file() else glob(f'{bkg["dir"]}/*.parquet', recursive=True)
                sum_genw_presel_tot = 0
                for file in tqdm(bkg_files[bkg['name']], desc=f'Reading sum_genw_presel for {bkg["name"]}', unit='files'):
                    sum_genw_presel_tot += float(pq.read_metadata(file).metadata[b'sum_genw_presel'])
                sum_genw_presel_bkg.append(sum_genw_presel_tot)
                print(f"Sum of genw_presel for {bkg['name']} is {sum_genw_presel_tot}. Now loading the files.")
                # load background files
                bkg_df = pd.read_parquet(bkg_files[bkg['name']], engine='auto', columns=columns_mc, filters=filters)
                bkg_df['bkg_type'] = i+1
                bkgs.append(bkg_df)
        
        # -- read the sum_genw_presel for DY
        sum_genw_presel_mc = 0
        dy_name = mc_dict.get('name', 'DYto2L')
        for file in tqdm(mc_files, desc=f'Reading sum_genw_presel for {dy_name}', unit='files'):
            sum_genw_presel_mc += float(pq.read_metadata(file).metadata[b'sum_genw_presel'])
        print(f"Sum of genw_presel for {dy_name} is {sum_genw_presel_mc}")

    # -- load the data and MC
    print(f'Loading data from {dir_dt} and DY from {dir_mc}')
    dt = pd.read_parquet(dt_files, engine='auto', columns=columns_dt, filters=filters) if dt_files else None
    dy = pd.read_parquet(mc_files, engine='auto', columns=columns_mc, filters=filters) if mc_files else None
    if backgrounds != []:
        if dt is not None:
            dt['bkg_type'] = 0
        if dy is not None:
            dy['bkg_type'] = 0
    if do_normalisation:
        mc = pd.concat([dy] + bkgs, ignore_index=True) if dy is not None else None
    else:
        mc = dy

    if dt is None and mc is None:
        raise AttributeError('One of the parameters dir_dt or dir_mc has to be set')

    if do_normalisation:
        # -- normalisation to the XS and luminosity
        luminosity = data_dict.get('luminosity', None)
        if luminosity is None :
            try :
                luminosity = normalisation['Lumi'][year+subyear]
            except KeyError:
                raise ValueError(f'Luminosity for year {year+subyear} not set in the config file')
            
        # -- normalisation of the DY
        mc['genWeight_normed'] = mc['genWeight']
        XS = mc_dict.get('XS', None) 
        if XS is None:
            try:
                XS = normalisation['XS'][dy_name] 
            except KeyError:
                raise ValueError(f'Cross section for {dy_name} not set in the config file')
        XSlumi = XS * luminosity / sum_genw_presel_mc
        print('Normalisation of the DY to the xsec and luminosity by a factor', XSlumi, f' using XS={normalisation["XS"][dy_name]} pb')
        mc.loc[mc['bkg_type'] == 0, 'genWeight_normed'] *= XSlumi
        mc.loc[mc['bkg_type'] == 0, 'weight'] *= XSlumi

        # -- normalisation of the backgrounds
        for i,bkg in enumerate(backgrounds):
            XS = bkg.get('XS', None) 
            if XS is None:
                try:
                    XS = normalisation['XS'][bkg['name']] 
                except KeyError:
                    raise ValueError(f'Cross section for {bkg["name"]} not set in the config file')
            XSlumi = XS  * luminosity / sum_genw_presel_bkg[i]
            print(f'Normalisation of the background {bkg["name"]} to the xsec and luminosity by a factor', XSlumi)
            mc.loc[mc['bkg_type'] == i+1, 'genWeight_normed'] *= XSlumi
            mc.loc[mc['bkg_type'] == i+1, 'weight'] *= XSlumi

    # -- apply the charge selection
    if charge:
        if dt is not None:
            dt = dt.query(f'lead_ele_charge * sublead_ele_charge == {charge}')
        if mc is not None:
            mc = mc.query(f'lead_ele_charge * sublead_ele_charge == {charge}')
    
    # -- add subyear tag
    if subyear is not None and subyear_list is not None:
        for df in [dt, mc]:
            if df is not None:
                for sub in subyear_list:
                    df[f'is_{sub}'] = subyear == sub

    # -- for electrons rename kinematic variables
    if is_ele:
        for df in [dt, mc]:
            if df is None:
                continue
            # -- for electron rename variables and recompute the di-lepton mass
            df['mgg'] = df['mass']
            df['mass'] = df.eval('mgg * sqrt(lead_ele_pt*sublead_ele_pt) / sqrt(lead_pt*sublead_pt)')
            df['lead_pho_pt'] = df['lead_pt']
            df['sublead_pho_pt'] = df['sublead_pt']
            df['lead_pt'] = df['lead_ele_pt']
            df['sublead_pt'] = df['sublead_ele_pt']
    
    # -- for electrons rename kinematic variables
    if remove_HDNA_SaS:
        for df in [dt, mc]:
            if df is None:
                continue
            # -- for electron rename variables and recompute the di-lepton mass
            df['mass_HDNA'] = df['mass']
            df['mass'] = df.eval('mass_HDNA * sqrt(lead_pt_raw*sublead_pt_raw) / sqrt(lead_pt*sublead_pt)')
            df['lead_HDNA_pt'] = df['lead_pt']
            df['sublead_HDNA_pt'] = df['sublead_pt']
            df['lead_pt'] = df['lead_pt_raw']
            df['sublead_pt'] = df['sublead_pt_raw']

    # -- if a correction lib file is provided correct the data scale
    if corrlib_scale:
        print(f"Energy re-scaling in data from corrlib file: {corrlib_scale['path']}")
        cset_path, cset_name = corrlib_scale['path'].split(':')
        scales = correctionlib.CorrectionSet.from_file(cset_path)[cset_name]
        scale_name = corrlib_scale.get('scale', None)
        
        args = (scale_name,) if scale_name is not None else ()
        args_lead = tuple(corrlib_scale['vars'])
        args_sublead = tuple(a.replace('lead', 'sublead') for a in args_lead)
        
        invert = corrlib_scale.get('invert', False)
        for pt_ele_name, args_ele in zip(['lead_pt', 'sublead_pt'], [args_lead, args_sublead]):
            corr_ele = scales.evaluate( *(args + tuple(dt[v_ele] for v_ele in args_ele)))
            if invert:
                corr_ele = 1./corr_ele
            dt[pt_ele_name] *= corr_ele
            dt['mass'] *= np.sqrt(corr_ele)
    
     # -- if a correction lib file is provided smear the MC
    if corrlib_smear:
        raise NotImplementedError('Smearing functionnality not yet implemented')

    # -- rename lead_var and sublead_var variables as var1 and var2
    for df in [dt, mc]:
        if df is None:
            continue
        for col in df.columns:
            if len(col) < 5:
                continue
            if "lead_" ==  col[:5]:
                v_name = col.split("lead_")[-1]
                df.rename(columns={col: f"{v_name}1"}, inplace=True)
            if "sublead_" in col:
                v_name = col.split("lead_")[-1]
                df.rename(columns={col: f"{v_name}2"}, inplace=True) 
        
        # -- add |ScEta| for categorisation 
        for ilep in [1, 2]:
            df[f'AbsScEta{ilep}'] = df[f'ScEta{ilep}'].abs()
            
        # -- filtering
        eta_cut = "AbsScEta1 < 2.5 and AbsScEta2 < 2.5 and ((AbsScEta1 < 1.4442) or (AbsScEta1 > 1.566)) and ((AbsScEta2 < 1.4442) or (AbsScEta2 > 1.566))"
        # eta_cut = "AbsScEta1 < 3.5"

        if selection is not None:
            print(f'Apply selection {selection}')
            selectionTot = f"{eta_cut} and {selection}" 
        else:
            print('Apply eta selection only')
            selectionTot = eta_cut

        df = df.query(selectionTot, inplace=True)
        

    # -- reweighting
    if mc is not None and dt is not None and do_reweight:
        print('Compute reweightings (ZPT, eta 2D) with selection :')
        print(reweight_selection if reweight_selection else '80 < mass < 100')
        #-- apply the reweighting to all MC events but compute it in the Z mass window
        mask_dt = dt.eval(reweight_selection if reweight_selection else '80 < mass < 100')
        mask_mc = mc.eval(reweight_selection if reweight_selection else '80 < mass < 100')

        # -- pileup reweighting
        if pileup_reweighting:
            print('Pileup reweighting')
            # mc['weight_pu'] = var1d_reweighter(dt.loc[mask_dt, 'fixedGridRhoAll'], mc['fixedGridRhoAll'], mc['weight'], 
            mc['weight_pu'] = var1d_reweighter(dt.loc[mask_dt, 'nPV'], mc['nPV'], mc['weight'], 
                                               bins_var=np.linspace(-0.5,63.5,33), mc_mask=mask_mc)
            mc['weight'] *= mc['weight_pu']
            mc['weight_central'] *= mc['weight_pu']

        # -- zpt reweighting
        mc['weight_z_pt'] = var1d_reweighter(dt.loc[mask_dt, 'pt'], mc['pt'], mc['weight'], 
                                             bins_var=bins_ptz_default, mc_mask=mask_mc)
        mc['weight'] *= mc['weight_z_pt']
    

        mc['weight_z_pt_central'] = var1d_reweighter(dt.loc[mask_dt,'pt'], mc['pt'], mc['weight_central'], 
                                                bins_var=bins_ptz_default, mc_mask=mask_mc)
        mc['weight_central'] *=  mc['weight_z_pt_central']

        # -- eta reweighting
        mc['weight_eta'] = var2d_reweighter(dt.loc[mask_dt, 'ScEta1'], dt.loc[mask_dt, 'ScEta2'], 
                                            mc['ScEta1'], mc['ScEta2'],
                                            bins_2d_var=(bins_eta_default, bins_eta_default),
                                            mc_weights=mc['weight'], mc_mask=mask_mc)
        mc[f'weight_no_eta'] = mc['weight']
        mc['weight'] *= mc['weight_eta']
    
        mc['weight_central_no_eta'] = mc['weight_central']
        mc['weight_central'] *= mc['weight_eta']

        # -- normalize the MC to the xsec
        norm_factor = dt.shape[0] / mc['weight'].sum()
        print(f'Normalize NLO MC with norm factor {norm_factor:.3g}')
        mc['weight'] *= norm_factor

        norm_factor = dt.shape[0] / mc['weight_central'].sum()
        print(f'Normalize LO MC with norm factor {norm_factor:.3g}')
        mc['weight_central'] *= norm_factor
        
    elif mc is not None:
        print('I will not reweight the ZpT in the simulation because no data are set')

    # -- saving the parquet file
    stem_out += ".ele" if is_ele else ".pho"    
    dir_out.mkdir(parents=True, exist_ok=True)
    if dt is not None and save_dt:
        print(f'Saving {dir_out / stem_out}.data.parquet')
        dt.to_parquet(dir_out / f"{stem_out}.data.parquet", engine="auto")
    if mc is not None and save_mc:
        print(f'Saving {dir_out / stem_out}.mc.parquet')
        mc.to_parquet(dir_out / f"{stem_out}.mc.parquet", engine="auto")


if __name__ == "__main__":
    main()
