import numpy as np
from . import data, design, fit, regressors


def ttest_1samp(X, popmean=0):

    dat = data.TrialGLMData(data=X-popmean, dim_labels=['x', 'y'])

    regs = list()
    regs.append(regressors.ConstantRegressor(num_observations=X.shape[0]))

    vals = np.zeros((len(regs),))
    vals[0] = 1
    contrasts = [design.Contrast(name='Mean', values=vals)]

    des = design.GLMDesign.initialise(regs, contrasts)
    model = fit.OLSModel(des, dat)

    return model.get_tstats()


def ttest_ind(X1, X2):

    X = np.concatenate((X1, X2), axis=0)

    group_vect = np.r_[np.ones((X1.shape[0],)), np.ones((X2.shape[0],))*2]

    dat = data.TrialGLMData(data=X, group_vect=group_vect)

    regs = list()
    regs.append(regressors.CategoricalRegressor(
            category_list=group_vect, codes=1, name='Group_1'))
    regs.append(regressors.CategoricalRegressor(
            category_list=group_vect, codes=2, name='Group_2'))

    contrasts = [design.Contrast(name='MainEffect', values=[1, -1])]

    des = design.GLMDesign.initialise(regs, contrasts)
    model = fit.OLSModel(des, dat)

    return model.get_tstats()


def ttest_paired(X1, X2):

    X = np.concatenate((X1, X2), axis=0)

    group_vect = np.r_[np.ones((X1.shape[0],)), np.ones((X2.shape[0],))*2]
    pair_vect = np.tile(np.arange(X2.shape[0]), 2)

    dat = data.TrialGLMData(data=X, group_vect=group_vect)

    regs = list()
    regs.append(regressors.CategoricalRegressor(
            category_list=group_vect, codes=1, name='Group_1', preproc='z'))
    for ii in range(pair_vect.max()+1):
        regs.append(regressors.CategoricalRegressor(
            category_list=pair_vect, codes=ii,
            name='Pair{0}'.format(ii), preproc=None))

    vals = np.zeros((len(regs),))
    vals[0] = 1
    contrasts = [design.Contrast(name='MainEffect', values=vals)]

    des = design.GLMDesign.initialise(regs, contrasts)
    model = fit.OLSModel(des, dat)

    return model.get_tstats()


def anova_1way(dataset, grouplabels):
    """Perform an one-way ANOVA test across data groups. The test is performed
    on the first dimension of the input data. The test is repeated for each
    additional dimension.

    The design is generated using the cell means model.

    Parameters
    ----------
    data : array_like
        array of data for each level.

    group_names : list or tuple of strings (optional)
        Identifing label for each sample

    Returns
    -------
    F: array_like
        F-statistics for group Main Effect

    des: design.GLMDesign object
        The specification of the test

    """

    # Specify design
    DC = design.DesignConfig()
    DC.add_mean_effects(grouplabels)

    for ii in range(len(np.unique(grouplabels))-1):
        vals = list(np.zeros((DC.num_regressors,)))
        vals[-1] = -1
        vals[ii] = 1
        DC.add_contrast(name=str(ii), values=vals)

    DC.add_ftest(name='MainEffect', values=list(np.repeat(1, DC.num_contrasts)))

    # Build data object and design
    info = {'category_list': grouplabels}
    dat = data.TrialGLMData(data=dataset, info=info)
    des = DC.design_from_datainfo(info)

    # Fit model
    model = fit.OLSModel(des, dat)

    return model.fstats, des


def anova_2factor(dataset, factor1, factor2, factor_names=['A', 'B']):
    """Perform a 2-factor ANOVA test across data groups. The test is performed
    on the first dimension of the input data. The test is repeated for each
    additional dimension.

    CURRENTLY LIMITED TO 2x2 DESIGNS!!

    Parameters
    ----------
    data : array_like
        array of data for each level.

    factor1_labels : list or tuple of strings (optional)
        vector specifing factor 1 level for each sample

    factor2_labels : list or tuple of strings (optional)
        vector specifing factor 2 level for each sample

    Returns
    -------
    F: array_like
        F-statistics for group Main Effect

    des: design.GLMDesign object
        The specification of the test


    """
    Au = np.unique(factor1)
    Bu = np.unique(factor2)

    grouplabels = np.zeros_like(factor1)
    gp_cnt = 0
    for ii in range(2):
        for jj in range(2):
            inds = (factor1 == Au[ii]) * (factor2 == Bu[jj])
            grouplabels[inds] = gp_cnt
            gp_cnt += 1

    # Specify design
    DC = design.DesignConfig()
    DC.add_mean_effects(grouplabels)

    DC.add_contrast(name='Main'+factor_names[0], values=[1, 1, -1, -1])
    DC.add_contrast(name='Main'+factor_names[1], values=[1, -1, 1, -1])
    DC.add_contrast(name='Interaction', values=[1, -1, -1, 1])

    DC.add_ftest(name='Main'+factor_names[0], values=[1, 0, 0])
    DC.add_ftest(name='Main'+factor_names[1], values=[0, 1, 0])
    DC.add_ftest(name='Interaction', values=[0, 0, 1])

    # Build data object and design
    info = {'category_list': grouplabels}
    dat = data.TrialGLMData(data=dataset, info=info)
    des = DC.design_from_datainfo(info)

    model = fit.OLSModel(des, dat)

    return model.fstats, des
