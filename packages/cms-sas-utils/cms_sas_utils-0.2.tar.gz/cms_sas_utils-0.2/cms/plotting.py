from ijazz.categorize import categorize
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import cms_fstyle as cms
import numpy as np
import pandas as pd
from typing import Union, List, Dict, Tuple

  

def create_fig(n_subfig: int=1) -> tuple[Figure, Figure]:
    """Create a figure with subfigures if requested

    Args:
        n_subfig (int, optional): number of sub-figures (either 1 or 2). Defaults to 1.

    Returns:
        tuple[Figure, Figure]: tuple of figures or subfigures when creating sub-figures
    """
    fig = plt.figure(figsize=(7 * n_subfig, 7), layout='constrained') 
    fig1 = fig
    fig2 = None
    if n_subfig > 1:
        fig1, fig2 = fig.subfigures(1, 2)
    return fig1, fig2


def plot_mll_data_per_cat(dt: pd.DataFrame, mc: List[pd.DataFrame], cut0:str=None,
                          mll_name1:str="mee", mll_name2: str=None, pt_name1:str=None, pt_name2:str=None, 
                          var_name:str=None, var_cats:str=None, var_latex:str=None, var_unit:str='',
                          mc_w_name:str=None, both_leptons=False, lead_electron=False, **kwargs) -> Tuple[List[Figure], Tuple[List[float], List[float]]]:
    """Make data/MC plot comparison of the di-lepton mass potentially in different categories based on the variable var_name.
    It can compare 2 different masses (before and after sas correction for instance).

    Args:
        dt (pd.DataFrame): dataframe containing the data with the mass variable and 
        mc (pd.DataFrame): _description_
        mll_name1 (str, optional): name of the di-lepton mass variable. Defaults to "mee".
        mll_name2 (str, optional): name of the second di-lepton mass variable. Defaults to None.
        cut0 (str, optional): cut to apply on the dataframes. Defaults to None.
        var_name (str, optional): name of the variable to categorize on (1 plot per category). Defaults to None.
        var_cats (str, optional): bining for the categorization. Defaults to None.
        var_latex (str, optional): latex string to display the categorisation var. Defaults to None.
        var_unit (str, optional): unit of the categorisation var. Defaults to ''.
        mc_w_name (str, optional): name of weight column in the mc dataframe. Defaults to None.
        yr_range (tuple, optional): y-range for the data/MC panel. Defaults to (0.75, 1.25).
        mll_bins (_type_, optional): bining for mll. Defaults to None.
        both_leptons(bool, optional): at least one lepton or both lepton in category. Defaults to False.
    """

    if isinstance(mc, pd.DataFrame):
        mc = [mc]

    if cut0 is None:
        cut0 = f"{mll_name1} > 40"  

    if mll_name2 is not None:
        if cut0 is None:
            cut02 = f"{mll_name2} > 40"
        else:
            cut02 = cut0
            if mll_name1 in cut0:
                cut02 = cut02.replace(mll_name1, mll_name2)
            if pt_name1 and pt_name2 and (pt_name1 in cut02):
                cut02 = cut02.replace(pt_name1, pt_name2)
            
    chi21 = []
    chi22 = []
    show_bkg = kwargs.get('show_bkg', False)
    n_subfig = 1 if mll_name2 is None else 2
    if var_name is None:
        idx_mc = mc[0].eval(cut0)
        idx_dt = dt.eval(cut0)
        mc_w = None if mc_w_name is None else mc[0].loc[idx_mc, mc_w_name]
        mcs = [mci.loc[idx_mc, mll_name1] for mci in mc]
        if show_bkg:
            mc_type = mc[0].loc[idx_mc, "bkg_type"]
        else:
            mc_type = None
        if f'{mll_name1}_scale_up' in mc[0].columns:
            print("Add syst with scale_up")
            mcs.append(mc[0].loc[idx_mc, f'{mll_name1}_scale_up'])
        if f'{mll_name1}_smear_up' in mc[0].columns:
            print("Add syst with smear_up")
            mcs.append(mc[0].loc[idx_mc, f'{mll_name1}_smear_up']) 
        fig1, fig2 = create_fig(n_subfig=n_subfig)
        y_range, chi2, ndof, mll_bins_out, hists = plot_data_mc_with_ratio([dt.loc[idx_dt, mll_name1]], mcs, mc_type=mc_type, mc_w=mc_w, fig=fig1, 
                                                                       **kwargs)
        chi21.append(chi2)                                 
        if mll_name2 is not None:
            idx_mc = mc[0].eval(cut02)
            idx_dt = dt.eval(cut02)
            mc_w = None if mc_w_name is None else mc[0].loc[idx_mc, mc_w_name]
            print(mll_name2, cut02)
            mcs = [mci.loc[idx_mc, mll_name2] for mci in mc]
            if show_bkg:
                mc_type = mc[0].loc[idx_mc, "bkg_type"]
            else:
                mc_type = None
            if f'{mll_name2}_scale_up' in mc[0].columns:
                print("Add syst with scale_up")
                mcs.append(mc[0].loc[idx_mc, f'{mll_name2}_scale_up'])
            if f'{mll_name2}_smear_up' in mc[0].columns:
                print("Add syst with smear_up")
                mcs.append(mc[0].loc[idx_mc, f'{mll_name2}_smear_up']) 
            
            kwargs['mll_bins'] = mll_bins_out
            kwargs['y_range'] = y_range
            _, chi2, ndof, _, hists2 = plot_data_mc_with_ratio([dt.loc[idx_dt, mll_name2]], mcs, mc_type=mc_type, mc_w=mc_w, fig=fig2, **kwargs)
            chi22.append(chi2)     
        if lead_electron:                            
            return [plt.gcf()], (chi21, chi22), [], []
        else:
            return [plt.gcf()], (chi21, chi22), (mll_bins_out, hists)

    if not isinstance(var_name, list):
        var_name = [var_name]
        var_cats = [var_cats]
        var_latex = [var_latex]
        var_unit = [var_unit]

    plot_categories = {f'{vname}': vcats for vname, vcats in zip(var_name, var_cats)}
    print(plot_categories)
    
    cat_dt = pd.Index(categorize(dt, category_dict=plot_categories, cut=cut0).flatten())
    cat_mc = pd.Index(categorize(mc[0], category_dict=plot_categories, cut=cut0).flatten())
    cat_plot = cat_dt.intersection(cat_mc)

    if mll_name2:
        if pt_name1 in plot_categories:
            # -- we want to keep the same order for keys
            keys = list(plot_categories.keys())
            values = list(plot_categories.values())
            index = keys.index(pt_name1)
            keys[index] = pt_name2
            plot_categories = dict(zip(keys, values))
            
        cat_dt = pd.Index(categorize(dt, category_dict=plot_categories, cut=cut02, prefix='cat2_').flatten())
        cat_mc = pd.Index(categorize(mc[0], category_dict=plot_categories, cut=cut02, prefix='cat2_').flatten())
        cat_plot2 = cat_dt.intersection(cat_mc)

    n_cat_bins = [len(bin)-1 for bin in var_cats]
    categories = np.arange(np.prod(n_cat_bins)).reshape(*n_cat_bins)

    if var_latex is None:
        var_latex = var_name
    figs = []
    cat_legends = []
    mll_bins_list = []
    hist_ijazz_list = []
    hist_egm_list = []
    for icat, cat in enumerate(cat_plot):
        cut = cut0 + f" and (cat1 == {cat} or cat2 == {cat})"
        if mll_name2:
            cut2 = cut02 + f" and (cat2_1 == {cat} or cat2_2 == {cat})"
        if both_leptons:
            cut = cut0 + f" and (cat1 == {cat} and cat2 == {cat})"
            if mll_name2:
                cut2 = cut02 + f" and (cat2_1 == {cat} and cat2_2 == {cat})"
        elif lead_electron:
            cut = cut0 + f" and (cat1 == {cat})"
            if mll_name2:
                cut2 = cut02 + f" and (cat2_1 == {cat})"
        fig1, fig2 = create_fig(n_subfig=n_subfig)

        idx_mc = mc[0].eval(cut)
        idx_dt = dt.eval(cut)
        cat_title = ''
        
        icats = np.unravel_index(icat, n_cat_bins) # get icat for each categories
        if var_unit == '':
            var_unit = [''] * len(var_name)

        if lead_electron:
            for icat, vcats, vlatex, vunit in zip(icats, var_cats, var_latex, var_unit):
                cat_title += f"${vcats[icat]:.3g} \leq${vlatex}$< {vcats[icat+1]:.3g}$ {vunit}\n"
            cat_legends.append(cat_title[:-2])
            cat_title = ''
        else:
            for icat, vcats, vlatex, vunit in zip(icats, var_cats, var_latex, var_unit):
                cat_title += f"${vcats[icat]:.3g} \leq${vlatex}$< {vcats[icat+1]:.3g}$ {vunit}\n"
            cat_title = cat_title[:-2]

        mc_w = None if mc_w_name is None else mc[0].loc[idx_mc, mc_w_name]
        mcs = [mci.loc[idx_mc, mll_name1] for mci in mc]
        if show_bkg:
            mc_type = mc[0].loc[idx_mc, "bkg_type"]
        else:
            mc_type = None
        if f'{mll_name1}_scale_up' in mc[0].columns:
            print("Add syst with scale_up")
            mcs.append(mc[0].loc[idx_mc, f'{mll_name1}_scale_up'])
        if f'{mll_name1}_smear_up' in mc[0].columns:
            print("Add syst with smear_up")
            mcs.append(mc[0].loc[idx_mc, f'{mll_name1}_smear_up'])    
        y_range, chi2, ndof, mll_bins_out, hists = plot_data_mc_with_ratio(dt.loc[idx_dt, mll_name1], mcs, mc_w=mc_w, mc_type=mc_type, fig=fig1, 
                                                                           title=cat_title, **kwargs)
        chi21.append(chi2/ndof)
        mll_bins_list.append(mll_bins_out)
        hist_ijazz_list.append(hists)
        if mll_name2 is not None:
            print(mll_name2,',', cut02)
            idx_mc = mc[0].eval(cut2)
            idx_dt = dt.eval(cut2)
            mc_w = None if mc_w_name is None else mc[0].loc[idx_mc, mc_w_name]
            mcs = [mci.loc[idx_mc, mll_name2] for mci in mc]
            if show_bkg:
                mc_type = mc[0].loc[idx_mc, "bkg_type"]
            else:
                mc_type = None
            if f'{mll_name2}_scale_up' in mc[0].columns:
                print("Add syst with scale_up")
                mcs.append(mc[0].loc[idx_mc, f'{mll_name2}_scale_up'])
            if f'{mll_name2}_smear_up' in mc[0].columns:
                print("Add syst with smear_up")
                mcs.append(mc[0].loc[idx_mc, f'{mll_name2}_smear_up'])

            kwargs2 = kwargs.copy()
            kwargs2['mll_bins'] = mll_bins_out
            kwargs2['y_range'] = y_range
            _, chi2, ndof, _, hists = plot_data_mc_with_ratio(dt.loc[idx_dt, mll_name2], mcs,  mc_w=mc_w, mc_type=mc_type, fig=fig2, 
                                                              title=cat_title,**kwargs2)
            chi22.append(chi2/ndof)
            hist_egm_list.append(hists)
        figs.append(plt.gcf())
    if lead_electron:
        return figs, (chi21, chi22), cat_legends, (mll_bins_list, hist_ijazz_list, hist_egm_list)
    else:
        return figs, (chi21, chi22), []
       

def plot_data_mc_with_ratio(dt: List[np.ndarray], mc: List[np.ndarray],mc_type: np.ndarray=None, mc_w:np.ndarray=None, fig:Figure=None,
                            mll_bins: Union[list, np.ndarray]=None, mll_latex: str='$m_{\ell\ell}$  (GeV)', mll_unit:str='GeV',
                            y_range:tuple[float, float]=None, y_scale:str='linear', yr_range = (0.8, 1.2), 
                            show_bkg:bool=False, show_median:bool=False, title: str=None) -> Tuple[Tuple[float, float], float, float]:
    """Make a plot with top panel: mll data vs MC, bottom panel, data/MC
    NB: the MC is normalised to data.

    Args:
        dt (np.ndarray): mll list for data
        mc (np.ndarray): mll list for mc
        mc_w (np.ndarray, optional): list of mc weights. Defaults to None.
        fig (plt.Figure, optional): figure or subfigure to plot on. Defaults to None.
        y_range (tuple, optional): y range top panel . Defaults to None.
        yr_range (tuple, optional): y range bottom pabel. Defaults to (0.75, 1.25).
        mll_bins (Union[list, np.ndarray], optional): bining. Defaults to None.
        title (str, optional): title to put on top on. Defaults to None.

    Returns: 
        Tuple[Tuple[float, float], float, float]: return a tuple with the ((y_range0, y_range_1), chi2, ndof)
    """

    if fig is None:
        fig = plt.figure(figsize=(7,7))
    fig.subplots_adjust(hspace=0, wspace=0)
    ax = fig.subplots(2, 1, sharex=True, height_ratios=(4, 1))

    bin_width = None
    if mll_bins is None:
        mll_bins = np.linspace(80, 100, 81)
    elif isinstance(mll_bins[-1], float):
        pass # already a bin array
    elif mll_bins[-1] in ['adaptative','a', 'adapt']:
        win_z_dt = (mll_bins[0], mll_bins[1])
        if len(dt)>0 and len(mc[0])>0:
            if isinstance(dt, list):
                dt_win = dt[0][(dt[0] > win_z_dt[0]) & (dt[0] < win_z_dt[1])]
            else:
                dt_win = dt[(dt > win_z_dt[0]) & (dt < win_z_dt[1])]
            mc_win = mc[0][(mc[0] > win_z_dt[0]) & (mc[0] < win_z_dt[1])]
            irq = np.subtract(*np.percentile(dt_win, [75, 25]))
            bin_width = max(2 * irq / np.power(len(mc_win),1/3), 0.25)
            n_bins = max(3,int(np.floor((win_z_dt[1]-win_z_dt[0])/bin_width)+1))
            bin_width = (win_z_dt[1]-win_z_dt[0])/(n_bins-1)
            mll_bins = np.linspace(*win_z_dt, n_bins)
        else:
            n_bins = 11
            bin_width = (win_z_dt[1]-win_z_dt[0])/(n_bins-1)
            mll_bins = np.linspace(*win_z_dt, n_bins)
    else:
        mll_bins = np.linspace(*mll_bins)

    if bin_width is None:
        bin_width = mll_bins[1] - mll_bins[0]

    x = mll_bins
    x_min = mll_bins[0]
    x_max = mll_bins[-1]
    range_x = (x_min, x_max)
    n_bins = len(mll_bins) - 1

    hmc, _ = np.histogram(mc[0], bins=n_bins, range=range_x, weights=mc_w)
    hmc_out = hmc
    hmc_count, _ = np.histogram(mc[0], bins=n_bins, range=range_x)
    hsyst = [np.histogram(my_mc, bins=n_bins, range=range_x, weights=mc_w)[0] for my_mc in mc[1:]]
    hdt, _ = np.histogram(dt, bins=n_bins, range=range_x)
    hmc = hmc.astype(np.float64)
    mc_norm = hdt.sum() / hmc.sum()
    # print(f"MC norm: {mc_norm}")
    
    if mc_w is not None:
        hmc_err, _ = np.histogram(mc[0], bins=n_bins, range=range_x, weights=mc_w**2)
        hmc_err = np.sqrt(hmc_err)*mc_norm
    else:
        hmc_err = np.sqrt(hmc)*mc_norm 

    hmc *= mc_norm
    hsyst = [hs * hdt.sum() / hs.sum() for hs in hsyst]

    
        
    syst_labels = ['scale_up','smear_up']
    colors = ['r','g']
    plt.sca(ax[0])

    def weighted_median(values, weights, mll_bins):
        # Apply the same mask to both values and weights
        mask = (values > mll_bins[0]) & (values < mll_bins[-1])
        filtered_values = values[mask]
        filtered_weights = weights[mask]
        i = np.argsort(filtered_values)
        sorted_values = filtered_values.iloc[i]
        sorted_weights = filtered_weights.iloc[i]
        c = np.cumsum(sorted_weights)
        median_idx = np.searchsorted(c, 0.5 * c.iloc[-1])
        return sorted_values.iloc[median_idx]

    if show_median:
        mc_median = weighted_median(mc[0], mc_w, mll_bins)
        if isinstance(dt, list):
            dt = dt[0]
        dt_median = dt[(dt > mll_bins[0]) & (dt < mll_bins[-1])].median()

    if not show_bkg:
        if show_median:
            cms.draw(x, hmc, yerr=hmc_err, option="H", legend=f"MC: {mc_median:.3f}", color="royalblue")
        else:
            cms.draw(x, hmc, yerr=hmc_err, option="H", legend=f"MC: {hmc_count.sum():.3e}".replace('e+0','e'), color="royalblue")
            # cms.draw(x, hmc, yerr=hmc_err, option="H", legend=f"MC: {hmc_count.sum()}".replace('e+0','e'), color="royalblue")
    if show_median:
        cms.draw(x, hdt, yerr=np.sqrt(hdt), option='E', color='k', legend=f"Data: {dt_median:.3f}")
    else:
        cms.draw(x, hdt, yerr=np.sqrt(hdt), option='E', color='k', legend=f"Data: {hdt.sum():.3e}".replace('e+0','e'))
        # cms.draw(x, hdt, yerr=np.sqrt(hdt), option='E', color='k', legend=f"Data: {hdt.sum()}".replace('e+0','e'))

    # -- show different bkgs
    if show_bkg:
        bkg_names = ['DYtoEE', 'DY TauTau', 'TT', 'VV', 'Wjets', 'QCD']
        bkg_colors = ['C0', 'C1', 'C2', 'C3', 'C4']
        bkg_types = np.sort(np.unique(mc_type))[::-1]
        bottom = np.zeros_like(hmc)
        for bkg_type in bkg_types:
            idx = mc_type == bkg_type
            hmc_bkg, _ = np.histogram(mc[0][idx], bins=n_bins, range=range_x, weights=mc_w[idx])
            hmc_bkg = hmc_bkg.astype(np.float64)
            hmc_bkg *= mc_norm
            xx = 0.5*(x[1:]+x[:-1])
            plt.sca(ax[0])
            plt.bar(xx, hmc_bkg, width=bin_width, bottom=bottom, alpha=0.5, label=bkg_names[bkg_type], color=bkg_colors[bkg_type])
            bottom += hmc_bkg

    # -- ratio plot
    plt.sca(ax[1])
    yerr2 = hmc_err**2
    for i,hs in enumerate(hsyst):
        yerr2 += (hs-hmc)**2
        # -- show each systematics
        # cms.draw(x, hs/hmc, option="E",legend=syst_labels[i], color=colors[i])
    
    cms.draw(x, np.ones(hmc.shape), yerr=np.sqrt(yerr2)/hmc, option="E1", color="gray")
    cms.draw(x, np.ones(hmc.shape), yerr=hmc_err/hmc, option="E1", color="royalblue")
    cms.draw(x, hdt/hmc, yerr=np.sqrt(hdt)/np.abs(hmc), option="E", color='k')
            

    # -- chi2 computation for binomial distribution
    # -- add MC normalisation to account for proper MC stat. power with weights
    # -- formula from https://online.stat.psu.edu/stat415/book/export/html/833
    yij = np.array([hdt, hmc * hmc.sum() / (hmc_err**2).sum()])
    yi = yij.sum(axis=1)
    yj = yij.sum(axis=0)
    n_tot = yi.sum()
    yi_yj_o_n = yi.reshape(-1, 1) * yj / n_tot
    mask = np.where(yi_yj_o_n !=0)
    if len(mask[0]) > 1:
        chi2 = ((yij[mask] - yi_yj_o_n[mask])**2 / yi_yj_o_n[mask]).sum() 
    else: 
        chi2 = 0

    ndof = int(len(mask[0])/2) - 1
    if y_range is None:
        y_range = list(ax[0].get_ylim())
        y_range[0] = 0
        y_range[1] *= 1.4

    if show_median:
        cms.polish_axis(ax=ax[0], y_range=y_range, y_title=f'Events/{bin_width:.2f} {mll_unit}', leg_title=f'$\chi^2/n_f$ = {chi2:.1f}/{ndof}\nMedian mass (GeV):', 
                        leg_loc='upper right', leg_title_fontsize='large', leg_fontsize='medium')
    else:
        cms.polish_axis(ax=ax[0], y_range=y_range, y_title=f'Events/{bin_width:.2f} {mll_unit}', leg_title=f'$\chi^2/n_f$ = {chi2:.1f}/{ndof}', leg_loc='upper right')
    cms.polish_axis(ax=ax[1], x_title=mll_latex, y_range=yr_range, y_title='data/MC')
    ax[0].set_title(title)
    ax[0].set_yscale(y_scale)
    if y_scale == "linear":
        ax[0].ticklabel_format(axis='y', style='sci', scilimits=(-2,2))
    else:
        y_range = list(ax[0].get_ylim())
        # y_range[0] = min(hdt.min(), hmc.min())/100
        y_range[0] = 2
        y_range[1] *= 100
        ax[0].set_ylim(y_range)

    
    return y_range, chi2, ndof, mll_bins, (hdt,hmc_count,hmc_out)
