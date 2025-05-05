# SaS utils

Package to convert file to IJazZ format, combine correction files and apply correction to parquet

## HiggsDNA Reader

This script, `reader_higgsdna.py`, is designed to read and convert HiggsDNA parquet files into the `ijazz_2p0` format. Below is a brief description of its main functions:

### Functions

#### `main()`
- **Description**: Entry point of the script. It reads the configuration file and calls the `read_and_convert` function with the appropriate parameters.
- **Usage**: `sas_reader_higgsdna config.yaml`

#### `read_and_convert()`
- **Description**: Reads and converts the HiggsDNA parquet file to the `ijazz_2p0` format.
- **Parameters**:
    - `data_dict` (dict): Dictionary containing data file information.
    - `mc_dict` (dict): Dictionary containing Monte Carlo (MC) file information.
    - `dir_out` (str): Output directory.
    - `stem_out` (str): Stem of the output file.
    - `is_ele` (bool): Flag to use GSF electron energy.
    - `mc_weight` (str): Name of the column containing the MC weights.
    - `corrlib_scale` (dict): Correction library to correct the energy scale in data.
    - `corrlib_smear` (dict): Correction library to smear the MC.
    - `add_vars` (List): Additional variables to include.
    - `charge` (int): Charge selection.
    - `selection` (str): Selection criteria.
    - `reweight_selection` (str): Reweighting selection criteria.
    - `pileup_reweighting` (bool): Flag to apply pileup reweighting.
    - `do_reweight` (bool): Flag to apply reweighting.
    - `subyear` (str): Subyear information.
    - `backgrounds` (list): List of background processes.
    - `year` (str): Year information.
    - `save_dt` (bool): Flag to save data.
    - `save_mc` (bool): Flag to save MC.

### Normalisation
- **Description**: Contains cross-section (XS) and luminosity (Lumi) values for different processes and years.

### MC weights
- **HiggsDNA**: 3 weights are saved:
  - `genWeight`: NLO weights from the generator
  - `weight` = `genWeight * weight_central`: NLO weights + reweight from HDNA
  - `weight_central`: reweight from HDNA ie `Pileup,..`

- Output of the reader: 
  - `genWeight`: NLO weights from the generator.
  - `weight` = `genWeight * weight_central * norm * RW`: NLO weights with HDNA and reader reweighting and normalization.
  - `genWeight_normed` = `genWeight * norm`: NLO weights from the generator normalized to the XS and luminosity.
  - `weight_central` = `weight_central * RW`: LO weights with HDNA and reader reweighting.

### Columns
- **Description**: Defines the columns for photons and electrons.

### Filters
- **Description**: Defines the filters for photons, electrons, and events.

### Usage Example
```bash
sas_reader_higgsdna config/cms/reader_higgsdna_example.yaml
```

This script is essential for converting and normalizing HiggsDNA data for further analysis in the `ijazz_2p0` framework using this example [reader_higgsdna_example.yaml](https://gitlab.cern.ch/pgaigne/sas_utils/-/blob/master/config/cms/reader_higgsdna_example.yaml).


## Combine corrlib

### combine_csets():
- **Description**: Combine different corrlib correction files, some files could use always the nominal scale for variations 
    (if only one variations should be considered to avoid double counting).
- **Parameters**:
    - `cset_files` (List[Union[str, Path]]): list of corrlib files
    - `icset_fix_scale` (Union[List,Tuple]): list of corrlib for which the nominal scale only should be use
    - `dir_results` (Union[str, Path]): directory
    - `dset_name` (str, optional): identfier of the datase. Defaults to 'DSET'.
    - `cset_version` (int, optional): version of the set of corrections. Defaults to 1.


### Usage Example
Combining the 6 steps:
```bash
file_corr0=TimeDep/EGMScalesSmearing_2022preEE.v1.json.gz
file_corr1=EtaR9/EGMScalesSmearing_2022preEE.v1.json.gz
file_corr2=FineEtaR9/EGMScalesSmearing_2022.v1.json.gz
file_corr3=PT/EGMScalesSmearing_2022.v1.json.gz
file_corr4=Gain/EGMScalesSmearing_2022.v1.json.gz
file_corr5=PTsplit/EGMScalesSmearing_2022preEE.v1.json.gz
```
```bash
    ijazz_corrlib_combine $file_corr0 $file_corr1 $file_corr2 $file_corr3 $file_corr4 $file_corr5 -i 1 2 3 4  -v 1 -o . -d Pho_2022preEE

```

Create `EGMScalesSmearing_Pho_2022preEE.v1.json.gz` output file. Including a compound correction for scales `EGMScale_Compound_Pho_2022preEE` and for each step, the scale correction :`EGMScale_Pho{step_name}_2022preEE` and smearing correction:`EGMSmearAndSyst_Pho{step_name}_2022preEE`.

We use `-i 1 2 3 4` because the systematics are computed in the last step (step5) and the time dependent correction does not include `escale` then we fix the `escale` for the file 1, 2, 3 and 4. Then `scale = scale0 * scale1 * scale2 * scale3 * scale4 * scale5` but `escale = escale5`


## Correct file

Apply Scale and Smearing to parquet files using this example [validation_samples.yaml](https://gitlab.cern.ch/pgaigne/sas_utils/-/blob/master/config/cms/validation_samples.yaml). Where we apply the compound scale on data and the smearing compute in the last step on MC.
```bash
sas_file_corrector config/cms/validation_samples.yaml
```