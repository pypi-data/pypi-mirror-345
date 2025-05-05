from pathlib import Path
import json
from typing import Dict, List, Tuple, Union
import pandas as pd
import correctionlib.schemav2 as cs
import argparse
import sys



def main():
    parser = argparse.ArgumentParser(description='Correction lib combined')
    parser.add_argument('cset_files', type=str, nargs='+' , help='list of input corrlib files')
    parser.add_argument('-i', '--ifix', type=int, default=-1, nargs='+', required=True, 
                        help='index of the correction for which the scale should be fixed in systematics (no variation).')
    parser.add_argument('-v', '--version', type=int, default=1, help='cset version')
    parser.add_argument('-d', '--dset', type=str, default="DSET", help='dataset identifier (i.e. Ele2022PostEE)')
    parser.add_argument('-o', '--outdir', type=str, default=".", help='output directory')

    args = parser.parse_args(sys.argv[1:])
    combine_csets(args.cset_files, icset_fix_scale=args.ifix, dir_results=args.outdir,
                  dset_name=args.dset, cset_version=args.version)


def open_corrlib_json(filename) -> Dict:
    """Read correction lib files from json

    Args:
        filename (str, Path): path to the json file (can gzip)

    Returns:
        Dict: dict with the correction in correction set
    """
    import gzip
    if Path(filename).suffix == '.gz':
        import gzip
        with gzip.open(filename) as fcorr:
            acset = json.load(fcorr)
    else:
        with open(filename) as fcorr:
            acset = json.load(fcorr)
    return acset


def fix_scale_set(acset: Dict):
    """
    Fix the scale in a correction set to the nominal value (i.e. default)
    This is done to avoid multiplying the up and down variation if one want to keep only 
    one set of systematic (as it should be the case for scale corrections)
    Args:
        acset (Dict): correction dictionnary a la correction lib
    """
    acset['inputs'] = [iin for iin in acset['inputs'] if iin['name'] != 'syst']
    for corr in acset['data']['content']:
        if corr['key'] == 'scale':
            acset['data'] = corr['value']
            break

def get_random_correction(random_variables:List[str]= ['pt', 'r9', 'ScEta', 'EventNumber'], cset_version=1):
    """Create a pseudo random generator correction to smear the MC. normal and stdflat distribution are correlated then we applied a transform on the first variable to decorrelate the two distributions.

    Args:
        random_variables (List[str], optional): input of the PRNG node. Defaults to ['pt', 'r9', 'ScEta', 'EventNumber'].
        cset_version (int, optional): Defaults to 1.

    Returns:
        cs.Correction: random correction 
    """
    return cs.Correction(name = f'EGMRandomGenerator', 
                            version = cset_version,
                            description='Pseudo random number generator for EGM corrections. It is used to smear the MC. stdnormal and stdflat distribution are included. The last one is useful for double gaussian smearing only.',
                            inputs = [cs.Variable(name="distribution", type="string", description="Distribution type")] +
                                     [cs.Variable(name=dim, type='real', description=dim) for dim in random_variables],
                            output = cs.Variable(name='random', type="real", description=f"Random value"),
                            data = cs.Category(nodetype='category',
                                                input='distribution',
                                                content=[cs.CategoryItem(key='stdnormal', # transform one input to avoid correlation between std normal and std flat
                                                                         value=cs.Transform(nodetype='transform',input='pt',
                                                                                            rule=cs.Formula(nodetype="formula",
                                                                                                               variables=random_variables[0:1],
                                                                                                               parser="TFormula",
                                                                                                               expression="x",
                                                                                                               ),
                                                                                            content=cs.HashPRNG(nodetype="hashprng",
                                                                                                                inputs=random_variables,
                                                                                                                distribution="normal", # stdnormal give different values on different machines 
                                                                                                                                       # https://github.com/cms-nanoAOD/correctionlib/issues/287
                                                                                                                )
                                                                                            )
                                                                        ),
                                                        cs.CategoryItem(key='stdflat',
                                                                        value=cs.Transform(nodetype='transform',input='pt',
                                                                                           rule=cs.Formula(nodetype="formula",
                                                                                                               variables=random_variables[0:1],
                                                                                                               parser="TFormula",
                                                                                                               expression="-x",
                                                                                                               ),
                                                                                            content=cs.HashPRNG(nodetype="hashprng",
                                                                                                                inputs=random_variables,
                                                                                                                distribution="stdflat",
                                                                                                                )
                                                                                            )
                                                                        )     
                                                        ]
                                                )
                            )


def combine_csets(cset_files:List[Union[str, Path]], icset_fix_scale:Union[List,Tuple], dir_results: Union[str, Path], 
                  dset_name:str='DSET', cset_version:int=1, include_random:bool=True):
    """Combine different corrlib correction files, some files could use always the nominal scale for variations 
    (if only one variations should be considered to avoid double counting).

    Args:
        cset_files (List[Union[str, Path]]): list of corrlib files
        icset_fix_scale (Union[List,Tuple]): list of corrlib for which the nominal scale only should be use
        dir_results (Union[str, Path]): directory
        dset_name (str, optional): identfier of the datase. Defaults to 'DSET'.
        cset_version (int, optional): version of the set of corrections. Defaults to 1.
    """

    csets = [open_corrlib_json(corr) for corr in cset_files]
    cset_description = csets[-1]['description'] # keep the description from last file
    csets = [cset['corrections'] for cset in csets]

    cset_smears = [corr  for cset in csets for corr in cset if 'smear' in corr['name'].lower()]
    cset_scales = [corr  for cset in csets for corr in cset if 'scale' in corr['name'].lower()]

    # -- get input (keep a unique set with 'syst' first)
    inputs = []
    inputs += [input for scale in cset_scales for input in scale['inputs']]
    df_inputs = pd.DataFrame({'name': [v['name'] for v in inputs], 'input': inputs}).drop_duplicates(subset=['name']).set_index('name')
    inputs_name = ['syst'] + [row for row in df_inputs.index if row != 'syst']
    inputs = df_inputs.loc[inputs_name, 'input'].tolist()

    for icset in icset_fix_scale:
        if icset >= 0:
            fix_scale_set(cset_scales[icset])

    # -- put all the corrections (smear and scales together and multiply all scales)
    # -- update pt if in the inputs
    inputs_update = [inp for inp in inputs_name if 'pt' in inp.lower()]      
    cset_final = cs.CorrectionSet(
            schema_version=2,
            corrections=cset_scales + cset_smears + ([get_random_correction()] if include_random else []),
            description=cset_description,
            compound_corrections=[
                cs.CompoundCorrection(
                    name=f"EGMScale_Compound_{dset_name}",
                    inputs=inputs,
                    output=cs.Variable(name='scale', type='real', description='Total EGM scale'),
                    inputs_update=inputs_update,
                    input_op='*',  # use corrected pt to compute the scale at each step
                    output_op='*',
                    stack=[cset['name'] for cset in cset_scales]
                    )
                ]
            )

    cset_names = [cset['name'] for cset in cset_scales+cset_smears] + [f"EGMScale_Compound_{dset_name}"]

    dir_results = Path(dir_results)
    file_out = dir_results / f"EGMScalesSmearing_{dset_name}{'_noHashPRNG' if not include_random else ''}.v{cset_version}.json"
    print(f"Writing out correction lib file: {file_out}.gz")
    print(f"containing: {cset_names}")
    print(f"    -> compound scale corr: {cset_names[-1]}")
    print(f"    -> compound input list: {inputs_name}")

    import gzip
    with gzip.open(f"{file_out}.gz", "wt") as fout:
        fout.write(cset_final.model_dump_json(indent=1,exclude_unset=True))
