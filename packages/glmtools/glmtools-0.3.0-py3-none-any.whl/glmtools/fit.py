# vim: set expandtab ts=4 sw=4:

import numpy as np
from copy import deepcopy
import multiprocessing as mp
from functools import partial
from scipy import ndimage, optimize, stats
from anamnesis import AbstractAnam, register_class

from . import util, viz


class AbstractModelFit(AbstractAnam):
    """
    Class for performing a GLM fit and storing results
    """

    hdf5_outputs = ['betas', 'copes', 'varcopes', 'coapes', 'fstats',
                    'beta_dimlabels', 'cope_dimlabels',
                    'good_observations', 'dof_error', 'dof_model',
                    'ss_total', 'ss_model', 'ss_error', 'time_dim',
                    'regressor_names', 'contrast_names', 'ftest_names']

    def __init__(self, design=None, data_obj=None, standardise_data=False, tags=None, fit_args=None):
        """Computes a GLM fit on a defined model and a dataset.

        Parameters
        ----------

        design : GLMDesign instance
            Design object defined by GLMDesign

        data_obj : TrialGLMData or ContinuousGLMData instance
            Data object defined by TrialGLMData or ContinuousGLMData

        standardise_data : boolean (optional, default=False)
            Boolean flag indicating whether to z-transform input data prior to
            fitting.

        Returns
        -------
            GLMFit instance

        """
        AbstractAnam.__init__(self)

        # In case we're initialising in a classmethod (probably a better solution for this somewhere...)
        if design is None or data_obj is None:
            return

        # Store fit args or initialise an empty dict
        self.fit_args = {} if fit_args is None else fit_args

        design.sanity_check()

        # Collapse all dimensions apart from the observations
        # Parameters and COPEs are returned in the original data dimensions at the end
        data = data_obj.get_2d_data()

        if standardise_data:
            data = util.standardise_data(data)
            self.is_standardised = True
        else:
            self.is_standardised = False

        # Store a copy of the design matrix
        self._design = design
        self.design_matrix = design.design_matrix
        self.regressor_list = design.regressor_list

        # Compute number of valid observations (observations with NaNs are ignored)
        self.good_observations = np.isnan(data.sum(axis=1)) == False  # noqa: E712

        # Adjust degrees of freedom for bad samples
        n_bad_samples = design.num_observations - self.good_observations.sum()
        self.dof_error = design.dof_error - n_bad_samples
        self.dof_model = self.dof_error - np.linalg.matrix_rank(self.design_matrix)

        # Run the actual fit
        self.compute_fit(design.design_matrix[self.good_observations, :],
                         data[self.good_observations, :],
                         design.contrasts,
                         fit_args=self.fit_args)

        # Set Absolue COPES
        self.coapes = np.abs(self.copes)

        # Compute sum squares for data and residuals
        self.ss_total = np.sum(np.power(data[self.good_observations, :], 2), axis=0)
        self.ss_model = np.sum(np.power(self.get_prediction(), 2), axis=0)
        self.ss_error = np.sum(np.power(self.get_residuals(data[self.good_observations, :]), 2), axis=0)

        # Compute F-tests if defined
        if design.ftests is None:
            self.fstats = None
        else:
            self.fstats = np.zeros((design.num_ftests, data.shape[1]))
            self.get_resid_dots(data[self.good_observations, :])

            for jj in range(design.num_ftests):
                cont_ind = design.ftests[jj, :].astype(bool)
                C = design.contrasts[cont_ind, :]
                D = design.design_matrix

                a = np.linalg.pinv(D.T.dot(D))
                b = np.linalg.pinv(np.linalg.multi_dot([C, a, C.T]))

                for ii in range(data.shape[1]):

                    B = self.betas[:, ii]
                    c = np.linalg.multi_dot([B.T, C.T, b, C, B])

                    num = c / np.linalg.matrix_rank(C)
                    denom = self.resid_dots[ii] / self.dof_error

                    self.fstats[jj, ii] = num / denom

        # Restore original data shapes
        self.betas = data_obj.unsquash_array(self.betas)
        self.copes = data_obj.unsquash_array(self.copes)
        self.coapes = data_obj.unsquash_array(self.coapes)
        self.varcopes = data_obj.unsquash_array(self.varcopes)
        if self.fstats is not None:
            self.fstats = data_obj.unsquash_array(self.fstats)

        self.ss_total = data_obj.unsquash_array(self.ss_total[None, :])
        self.ss_error = data_obj.unsquash_array(self.ss_error[None, :])
        self.ss_model = data_obj.unsquash_array(self.ss_model[None, :])

        self.regressor_names = design.regressor_names
        self.contrast_names = design.contrast_names
        self.ftest_names = design.ftest_names
        if 'time_dim' in data_obj.info and data_obj.info['time_dim'] is not None:
            self.time_dim = data_obj.info['time_dim']
        else:
            self.time_dim = None
        self.tags = tags

        self.beta_dimlabels = list(('Regressors',
                                    *data_obj.info['dim_labels'][1:]))
        self.cope_dimlabels = list(('Contrasts',
                                    *data_obj.info['dim_labels'][1:]))
        self.tstat_dimlabels = list(('Contrasts',
                                     *data_obj.info['dim_labels'][1:]))

    def compute_betas(self, design_matrix, data, fit_args=None):

        raise NotImplementedError('This is an abstract class, please use OLSModel')

    def get_prediction(self, X=None):

        if X is None:
            X = self.design_matrix[self.good_observations, :]

        betas = np.reshape(self.betas, (self.betas.shape[0], np.prod(self.betas.shape[1:])))

        pred = X.dot(betas)

        return np.reshape(pred, (pred.shape[0], *self.betas.shape[1:]))

    def get_residuals(self, data):
        return data - self.get_prediction()

    def get_cookdist(self, data):
        return compute_cookDistance(self.design_matrix, data)

    def get_shapiro(self, data):

        resids = self.get_residuals(data)
        orig_shape = resids.shape

        resids = resids.reshape(resids.shape[0], -1)

        shap = np.zeros((resids.shape[1],))
        for ii in range(len(shap)):
            shap[ii], _ = stats.shapiro(resids[:, ii])

        return shap.reshape(orig_shape[1:])

    def get_studentized_residuals(self, data):

        return self.get_residuals(data) / self.mse / np.sqrt(1 - self._design.leverage)[:, None]

    def get_resid_dots(self, data):
        resid = self.get_residuals(data)
        self.resid_dots = np.einsum('ij,ji->i', resid.T, resid)

    def get_tstats(self, varcope_smoothing=None, smooth_dims=None,
                   window_size=11, hat_factor=None):
        """Computes t-statistics from COPEs in a fitted model, may add optional
        temporal varcope smoothing.

        Parameters
        ----------

        varcope_smoothing : {None, int} (optional, default=None)
            Optional window length for varcope smoothing of time dimension. The
            default is no smoothing as indicated by None.

        smoothing_window : {np.hanning,np.bartlett,np.blackman,np.hamming} default=np.hanning
            One of numpys window functions to apply during smoothing. Ignored
            if varcope_smoothing=None

        Returns
        -------

        ndarray
            Array containing t-statistic estimates

        """
        return get_tstats(self.copes, self.varcopes.copy(),
                          varcope_smoothing=varcope_smoothing, smooth_dims=smooth_dims,
                          window_size=window_size, hat_factor=hat_factor)

    def project_range(self, contrast, nsteps=2, values=None, mean_ind=0):
        """Get model prediction for a range of values across one regressor."""

        steps = np.linspace(self.design_matrix[:, contrast].min(),
                            self.design_matrix[:, contrast].max(),
                            nsteps)
        pred = np.zeros((nsteps, *self.betas.shape[1:]))

        # Run projection
        for ii in range(nsteps):
            if nsteps == 1:
                coeff = 0
            else:
                coeff = steps[ii]
            pred[ii, ...] = self.betas[mean_ind, ...] + coeff*self.betas[contrast, ...]

        # Compute label values
        if nsteps > 1:
            scale = self.regressor_list[contrast].values_orig
            llabels = np.linspace(scale.min(), scale.max(), nsteps)
        else:
            llabels = ['Mean']

        return pred, llabels

    @property
    def num_observations(self):

        return self.design_matrix.shape[0]

    @property
    def num_regressors(self):

        return self.betas.shape[0]

    @property
    def tstats(self):
        return get_tstats(self.copes, self.varcopes)

    @property
    def num_contrasts(self):

        return self.copes.shape[0]

    @property
    def num_tests(self):

        return self.betas.shape[1]

    @property
    def mse(self):

        return self.ss_error / self.dof_error

    @property
    def r_square(self):

        return 1 - (self.ss_error / self.ss_total)

    @property
    def cooks_distance(self, data):
        """https://en.wikipedia.org/wiki/Cook%27s_distance"""

        raise RuntimeError

        # Leverage per observation
        hat_diag = self._design.leverage
        term2 = hat_diag / ((1 - hat_diag)**2)

        return term2

    @property
    def log_likelihood(self):

        raise NotImplementedError('This is an abstract class')

    @property
    def aic(self):
        # Returns the Akaike Information Criterion of model fit:
        """www.wikipedia.com/en/Akaike_information_criterion"""
        return 2*(self.num_regressors+1) - 2*self.log_likelihood()

    @property
    def bic(self):
        # Returns the Bayesian Information Criterion of model fit:
        """www.wikipedia.com/en/Bayesian_information_criterion"""
        return (self.num_regressors+1)*np.log(self.num_observations) - 2*self.log_likelihood()

    @classmethod
    def load_from_hdf5(cls, hdfpath):

        # This function will be removed soon but keeping it for reference atm.
        # Raise a warning if someone happens to use it
        raise DeprecationWarning('Please use Anamnesis API instead!')

        ret = cls()

        import h5py
        f = h5py.File(hdfpath)

        ret.betas = f['OLSModel/betas'][...]
        ret.copes = f['OLSModel/copes'][...]
        ret.coapes = f['OLSModel/coapes'][...]
        ret.varcopes = f['OLSModel/varcopes'][...]

        ret.ss_total = f['OLSModel/ss_total'][...]
        ret.ss_error = f['OLSModel/ss_error'][...]
        ret.ss_model = f['OLSModel/ss_model'][...]

        if 'fstats' in f['OLSModel'].keys():
            ret.fstats = f['OLSModel/fstats'][...]
            ret.ftest_names = list(f['OLSModel/ftest_names'][...])
        else:
            ret.fstats = None
            ret.ftest_names = None

        ret.regressor_names = list(f['OLSModel/regressor_names'][...])
        ret.contrast_names = list(f['OLSModel/contrast_names'][...])
        ret.beta_dimlabels = tuple(f['OLSModel/beta_dimlabels'][...])
        ret.cope_dimlabels = tuple(f['OLSModel/cope_dimlabels'][...])

        ret.good_observations = f['OLSModel/good_observations'][...]

        ret.dof_error = f['OLSModel'].attrs['dof_error']
        ret.dof_model = f['OLSModel'].attrs['dof_model']

        ret.time_dim = f['OLSModel'].attrs['time_dim']

        return ret


register_class(AbstractModelFit)

# ------------------------------------------------------------------------
# t-stats and corrections


def _get_varcope_thresh2(vc, factor=2):
    from sklearn.mixture import GaussianMixture
    vc = np.log(vc.reshape(-1, 1))
    gm = GaussianMixture(n_components=2, random_state=0).fit(vc)
    x = np.linspace(vc.min(), vc.max(), 100000)
    preds = gm.predict(x.reshape(-1, 1))
    thresh = np.where(np.diff(preds) != 0)[0][0]
    thresh = x[thresh]
    return np.exp(thresh)*factor


def varcope_corr_hat(vc, factor=1e-3, pooled_dims=None):
    # https://www.sciencedirect.com/science/article/pii/S1053811911011906#s0010
    if pooled_dims is None:
        pooled_dims = np.arange(vc.ndim)
    elif isinstance(pooled_dims, (float, int)):
        pooled_dims = [pooled_dims]

    delta = factor * vc.max(axis=tuple(pooled_dims))
    print('Clipping varcopes at {} {}'.format(delta, delta.shape))

    to_shape = np.array(vc.shape)
    to_shape[list(pooled_dims)] = 1

    vc = vc + np.broadcast_to(np.reshape(delta, to_shape), vc.shape)

    return vc


def varcope_corr_medfilt(vc, window_size=11, smooth_dims=None):
    if smooth_dims is None:
        smooth_dims = np.arange(vc.ndim)
    elif isinstance(smooth_dims, (float, int)):
        smooth_dims = [smooth_dims]
    print('Applying medfilt smoothing of {} to dims {} of {}'.format(window_size, smooth_dims, vc.shape))

    sigma = np.ones((vc.ndim,), dtype=int)
    sigma[np.array(smooth_dims)] = window_size

    return ndimage.median_filter(vc, sigma)


def varcope_corr_avg(vc, smooth_dims=None):
    if smooth_dims is None:
        smooth_dims = np.arange(vc.ndim)
    elif isinstance(smooth_dims, (float, int)):
        smooth_dims = [smooth_dims]
    print('Averaging varcopes over dims {}'.format(smooth_dims))

    avg_vc = np.mean(vc, axis=tuple(smooth_dims))

    # Broadcast back to correct shape
    to_shape = np.array(vc.shape)
    to_shape[list(smooth_dims)] = 1

    return np.broadcast_to(np.reshape(avg_vc, to_shape), vc.shape)


def varcope_corr_gaussfilt(vc, window_size, smooth_dims=None):
    if smooth_dims is None:
        smooth_dims = np.arange(vc.ndim)
    elif isinstance(smooth_dims, (float, int)):
        smooth_dims = [smooth_dims]
    print('Applying gaussian smoothing of {} to dims {}'.format(window_size, smooth_dims))

    sigma = np.zeros((vc.ndim,))
    sigma[np.array(smooth_dims)] = window_size
    return ndimage.gaussian_filter(vc, sigma)


def get_tstats(copes, varcopes,
               varcope_smoothing=None, smooth_dims=None,
               window_size=11, hat_factor=None):
    """Computes t-statistics from COPEs in a fitted model, may add optional
    varcope smoothing.

    Parameters
    ----------

    varcope_smoothing : {None, int} (optional, default=None)
        Optional window length for varcope smoothing of time dimension. The
        default is no smoothing as indicated by None.

    smoothing_window : {np.hanning,np.bartlett,np.blackman,np.hamming} default=np.hanning
        One of numpys window functions to apply during smoothing. Ignored
        if varcope_smoothing=None

    Returns
    -------

    ndarray
        Array containing t-statistic estimates

    """

    varcopes = varcopes.copy()  # before we do any corrections...

    if hat_factor is not None:
        varcopes = varcope_corr_hat(varcopes, factor=hat_factor)

    if varcope_smoothing == 'medfilt':
        varcopes = varcope_corr_medfilt(varcopes, window_size, smooth_dims)
    elif varcope_smoothing == 'gaussfilt':
        varcopes = varcope_corr_gaussfilt(varcopes, window_size, smooth_dims)
    elif varcope_smoothing == 'avg':
        varcopes = varcope_corr_avg(varcopes, smooth_dims)

    denom = np.sqrt(varcopes)

    # Compute t-values
    # run this in where to avoid RunTimeWarnings
    tstats = np.where(np.isnan(denom) == False,  # noqa: E712
                      copes / denom,
                      np.nan)  # noqa E712
    return tstats


# ------------------------------------------------------------------------
# Effect Size & Power


def cohens_f2(design, data, reg_idx, model=None):
    """ Compute effect sizes associated with a specific regressor.

    Parameters
    ----------
    design : GLMDesign instance
        Design object defined by GLMDesign
    data : TrialGLMData or ContinuousGLMData instance
        Data object defined by TrialGLMData or ContinuousGLMData
    reg_idx : int
        The index of the regressor of interest
    model : OLSModel instance
        GLM model object - optional, will be recomputed from design and data if not passed in.

    Returns
    -------
    array
        Cohens F-squared values

    """
    from glmtools.fit import OLSModel
    if model is None:
        model = OLSModel(design, data)

    cf2 = np.zeros_like(model.betas)
    denom = 1 - model.r_square

    small_design = deepcopy(design)

    small_design.design_matrix = np.delete(small_design.design_matrix, reg_idx, axis=1)
    small_design.contrasts = np.delete(small_design.contrasts, reg_idx, axis=1)
    small_model = OLSModel(design=small_design, data_obj=data)

    cf2 = (model.r_square - small_model.r_square) / denom

    return cf2


def cohens_f2_compute_power(f2, num_regressors, num_observations, siglevel=0.05):
    """
    Calculate the power of an effect from a general linear model (GLM) regression.

    Parameters
    ----------
    f2 : array_like
        Cohen's F-squared values
    num_observations : int
        Number of data points in dataset
    num_regressors : int
        Number of regressors in model
    siglevel : float (0 < siglevel < 1)
        The desired significance level (alpha) of the test (default is 0.05)

    Returns
    -------
    array
        The power values corresponding to the input parameters

    """
    ncp = f2*(num_regressors+num_observations+1)
    tmp = stats.f.ppf(1 - siglevel, num_regressors, num_observations)
    return 1 - stats.ncf.cdf(tmp, num_regressors, num_observations, ncp)


def cohens_f2_compute_sample_size(f2, num_regressors, siglevel=0.05, power=80, max_N=1000):
    """
    Calculate sample size required to achieve a given power
    for general linear model (GLM) regression.

    Note that this function is a numerical approximation using `scipy.optimize.brentq`.

    Parameters
    ----------
    f2 : array_like
        Cohen's F-squared values
    num_regressors : int
        Number of regressors in model
    siglevel : float (0 < siglevel < 1)
        The desired significance level (alpha) of the test (default is 0.05)
    power : float (0 < siglevel < 100)
        The desired statistical power as a percentage (default is 80)
    max_N : int
        The largest sample size that can be assessed.
        The routine will stop looking at this value (default is 1000).

    Returns
    -------
    array
        The sample size values corresponding to the input parameters

    """

    def func(num_observations, num_regressors, f2, siglevel, power):
        tmp = stats.f.ppf(1 - siglevel, num_regressors, num_observations)
        ncp = f2*(num_regressors+num_observations+1)
        return 1 - stats.ncf.cdf(tmp, num_regressors, num_observations, ncp) - power

    def run_brentq(func, min_N, max_N, args=None):
        try:
            return optimize.brentq(func, min_N, max_N, args=args)
        except ValueError:
            return np.nan

    if np.array(f2).size == 1:
        args = (num_regressors, f2, siglevel, power)
        return run_brentq(func, 1, max_N, args=args)
    else:
        # loop over items in input array
        f2_flat = np.array(f2).reshape(-1)
        sample_size = np.zeros_like(f2_flat)
        for ii in range(f2_flat.shape[0]):
            args = (num_regressors, f2_flat[ii], siglevel, power)
            sample_size[ii] = run_brentq(func, 1, max_N, args=args)

        return sample_size.reshape(f2.shape)


def cohens_f2_compute_effect_size(num_observations, num_regressors, siglevel=0.05, power=80):
    """
    Calculate sample size required to achieve a given power
    for general linear model (GLM) regression.

    Note that this function is a numerical approximation using `scipy.optimize.brentq`.

    Parameters
    ----------
    num_observations : int
        Number of data points in dataset
    num_regressors : int
        Number of regressors in model
    siglevel : float (0 < siglevel < 1)
        The desired significance level (alpha) of the test (default is 0.05)
    power : float (0 < siglevel < 100)
        The desired statistical power as a percentage (default is 80)

    Returns
    -------
    array
        The Cohens F-squared values corresponding to the input parameters

    """

    def func(f2, num_observations, num_regressors, siglevel, power):
        return cohens_f2_compute_power(f2, num_regressors, num_observations, siglevel) - power

    def run_brentq(func, min_f2, max_f2, args=None):
        try:
            return optimize.brentq(func, min_f2, max_f2, args=args)
        except ValueError:
            return np.nan

    if np.array(num_observations).size == 1:
        args = (num_observations, num_regressors, siglevel, power)
        return run_brentq(func, 0, 1, args=args)
    else:
        # loop over items in input array
        num_observations_flat = np.array(num_observations).reshape(-1)
        effect_size = np.zeros_like(num_observations_flat)
        for ii in range(num_observations_flat.shape[0]):
            args = (num_regressors, num_observations_flat[ii], siglevel, power)
            effect_size[ii] = run_brentq(func, 0, 1, args=args)

        return effect_size.reshape(num_observations.shape)

# ------------------------------------------------------------------------
# OLS Implementation


def _get_prediction(design_matrix, betas):
    return design_matrix.dot(betas)


def _get_residuals(design_matrix, betas, data):
    return data - _get_prediction(design_matrix, betas)


def ols_fit(design_matrix, data, contrasts, method='pinv', weights=None):
    """Fit a Ordinary Least Squares fit."""
    from glmtools.fit import (compute_betas_pinv,
                              compute_betas_numpy_lstsq,
                              compute_ols_contrasts,
                              compute_ols_varcopes)

    if method == 'pinv':
        betas = compute_betas_pinv(design_matrix, data)
    elif method == 'numpy_lstsq':
        betas = compute_betas_numpy_lstsq(design_matrix, data)
    elif method == 'positive':
        betas = compute_betas_nnls(design_matrix, data)
    elif method == 'wols':
        betas = compute_betas_wols(design_matrix, data, weights)
    else:
        print(method)

    copes = compute_ols_contrasts(contrasts, betas)

    varcopes = compute_ols_varcopes(design_matrix, data, contrasts, betas)

    return betas, copes, varcopes


def compute_betas_pinv(design_matrix, data):
    # Invert design matrix
    design_matrix_inv = np.linalg.pinv(design_matrix)

    # Estimate betas
    return design_matrix_inv.dot(data)


def compute_betas_numpy_lstsq(design_matrix, data):
    b, residuals, rank, s = np.linalg.lstsq(design_matrix, data)
    return b


def compute_betas_nnls(design_matrix, data):

    if data.shape[1] == 1:
        betas = optimize.nnls(design_matrix, data)
    else:
        P = mp.Pool(processes=6)
        args = [(design_matrix, data[:, ii]) for ii in range(data.shape[1])]
        res = P.starmap(optimize.nnls, args)
        P.close()

        betas = np.vstack([res[ii][0] for ii in range(data.shape[1])]).T
        #rnorm = np.vstack([res[ii][1] for ii in range(data.shape[1])])

    return betas


def compute_betas_wols(design_matrix, data, weights):
    from sklearn.linear_model import LinearRegression

    reg = LinearRegression().fit(design_matrix, data, sample_weight=weights)

    return reg.coef_.T


def compute_ols_contrasts(contrasts, betas):
    # Compute contrasts
    copes = contrasts.dot(betas)

    return copes


def compute_ols_varcopes(design_matrix, data, contrasts, betas):

    # Compute varcopes
    varcopes = np.zeros((contrasts.shape[0], data.shape[1]))

    # Compute varcopes
    residue_forming_matrix = np.linalg.pinv(design_matrix.T.dot(design_matrix))
    var_forming_matrix = np.diag(np.linalg.multi_dot([contrasts,
                                                     residue_forming_matrix,
                                                     contrasts.T]))

    # This is equivalent to >> np.diag( resid.T.dot(resid) )
    resid = _get_residuals(design_matrix, betas, data)
    resid_dots = np.einsum('ij,ji->i', resid.T, resid)
    del resid
    dof_error = data.shape[0] - np.linalg.matrix_rank(design_matrix)
    V = resid_dots / dof_error
    varcopes = var_forming_matrix[:, None] * V[None, :]

    return varcopes


class OLSModel(AbstractModelFit):

    def compute_fit(self, design_matrix, data, contrasts, fit_args=None):

        b, c, v = ols_fit(design_matrix, data, contrasts, **fit_args)
        self.betas = b
        self.copes = c
        self.coapes = np.abs(c)
        self.varcopes = v

    def log_likelihood(self):
        # Computes the total model log likehood, which is the sum of each observation's log likelihood given by:
        # L(i) = -0.5 * log(2*pi*sigma_sq) - 0.5*(y(i)-X(i,:)B).^2/sigma_sq
        # ll = sum(i to N) L(i)
        #
        # where sigma_sq is the variance of the residuals, y(i) is the ith datapoint, X(i) the ith row of
        # the design matrix, and B the OLS coefficients.

        ll = - self.num_observations / 2.
        ll = ll - 0.5*self.num_observations*np.log(2*np.pi*self.ss_error/self.num_observations)
        return ll


register_class(OLSModel)


def run_regressor_selection(design, data, mode='forward'):
    # Run a new model dropping each regressor in turn
    models = [OLSModel(design, data)]

    for ii in range(design.num_regressors):
        if mode == 'forward':
            # Keep only regressor ii
            inds = np.setdiff1d(np.arange(design.num_regressors), ii)
            small_design = deepcopy(design)
            small_design.design_matrix = np.delete(small_design.design_matrix, inds, axis=1)
            small_design.contrasts = np.delete(small_design.contrasts, inds, axis=1)
            rname = small_design.regressor_names[ii]
            small_design.regressor_names = [rname]
            reg = small_design.regressor_list[ii]
            small_design.regressor_list = [reg]
            print("Keeping '{0}'".format(rname))

            small_model = OLSModel(small_design, data)

        elif mode == 'backward':
            # Delete regressor ii
            small_design = deepcopy(design)
            small_design.design_matrix = np.delete(small_design.design_matrix, ii, axis=1)
            small_design.contrasts = np.delete(small_design.contrasts, ii, axis=1)
            rname = small_design.regressor_names.pop(ii)
            reg = small_design.regressor_list.pop(ii)
            print("Dropping '{0}'".format(rname))

            small_model = OLSModel(small_design, data)

        viz.summarise_regressor_list(small_design.regressor_list)
        print('\n')
        models.append(small_model)

    return models


# ---------------------------------------------------------
# sklearn functions


def skl_fit(design_matrix, data, contrasts, estimator=None, sample_weight=None):
    """Fit using a paramatrised SK-Learn object."""

    if estimator is None:
        from sklearn import linear_model
        estimator = linear_model.LinearRegression

    betas, skm = _fit_sk(estimator, design_matrix, data, sample_weight=sample_weight)

    copes, coapes = compute_ols_contrasts(contrasts, betas)

    varcopes = compute_ols_varcopes(design_matrix, data, contrasts, betas)

    return betas, copes, varcopes, skm


class SKLModel(AbstractModelFit):

    def compute_fit(self, design_matrix, data, fit_args=None):
        from sklearn import linear_model

        if fit_args is None:
            fit_args = {'lm': 'LinearRegression'}

        # Always assume that the design matrix has this right
        if 'fit_intercept' not in fit_args:
            fit_args['fit_intercept'] = False

        self.fit_args = fit_args.copy()

        # Actual model fit
        rtype = fit_args.pop('lm')
        batch = fit_args.pop('batch', 'sklearn')
        njobs = fit_args.pop('njobs', 1)
        reg = getattr(linear_model, rtype)

        if rtype == 'RANSACRegressor':
            # We need to pass in a base estimator
            base_estimator = linear_model.LinearRegression(**fit_args)
            reg = reg(base_estimator=base_estimator)
        else:
            reg = reg(**fit_args)

        if batch == 'sklearn':
            # Use sklearns internal batching - this considers all features
            # together. For instance, outliers will be detected across the
            # whole dataset

            self.betas, self.skm = _fit_sk(reg, design_matrix, data)

        else:
            # Use an external batching loop - this will consider each
            # regression as a separate entity. For instance, outliers are
            # detected independantly in each 'feature'

            args = [(reg, design_matrix, data[:, ii]) for ii in range(data.shape[1])]

            import multiprocessing as mp
            p = mp.Pool(processes=njobs)

            res = p.starmap(_fit_sk, args)

            self.betas = np.concatenate(([r[0] for r in res]), axis=1)
            self.skm = [r[1] for r in res]


register_class(SKLModel)


class SKLModel2(AbstractModelFit):

    def compute_fit(self, design_matrix, data, contrasts, fit_args=None):
        from sklearn import linear_model
        skl_fitter = fit_args.pop('fitter', None)
        if skl_fitter is None:
            skl_fitter = linear_model.LinearRegression(fit_intercept=False)

        self.betas, self.skm = _fit_sk(skl_fitter, design_matrix, data, **fit_args)

        self.copes = compute_ols_contrasts(contrasts, self.betas)

        self.varcopes = compute_ols_varcopes(design_matrix, data, contrasts, self.betas)


def _fit_sk(reg, design_matrix, data, sample_weight=None):

    skm = reg.fit(X=design_matrix, y=data, sample_weight=sample_weight)
    if hasattr(skm, 'coef_'):
        betas = skm.coef_.T
    elif hasattr(skm, 'estimator_') and hasattr(skm.estimator_, 'coef_'):
        betas = skm.estimator_.coef_.T

    if betas.ndim == 1:
        betas = betas[:, None]

    return betas, skm


# ---------------------------------------------------------
# Flame1 functions


def logbetafunctionnew(x, y, z, S):
    iU = np.diag(1 / (S + np.exp(x)))
    ziUz = z.T.dot(iU).dot(z)
    gam = np.linalg.inv(ziUz).dot(z.T).dot(iU).dot(y)
    ret = -(0.5*np.log(np.linalg.det(iU)) - 0.5*np.log(np.linalg.det(ziUz)) -
            0.5*(y.T.dot(iU).dot(y) - gam.T.dot(ziUz).dot(gam)))
    return ret


def _run_flame1(y, z, S, contrasts, fixed=False):
    """Solve GLM y=z*gam+e where e~N(0, beta+diag(S)) using FLAME1.

    Fast-posterior approximation using section 3.5 & 10.7 of
    https://www.fmrib.ox.ac.uk/datasets/techrep/tr03mw1/tr03mw1.pdf
    """

    opt_func = partial(logbetafunctionnew, y=y, z=z, S=S)

    if fixed:
        beta = 0
    else:
        # Brent's algorithm solving eqn 45
        res = optimize.minimize_scalar(opt_func, method='brent')
        if res.success is False:
            print('Brent Fail!')
        beta = np.exp(res.x)

    iU = np.diag((1 / (S + beta)))

    covgam = np.linalg.pinv(z.T.dot(iU).dot(z))
    gam = covgam.dot(z.T).dot(iU).dot(y)

    cope = contrasts.dot(gam)
    varcope = contrasts.dot(covgam).dot(contrasts.T)
    return gam, cope, varcope


def flame1(design_matrix, data, S, contrasts, fixed=False, nprocesses=1):

    if data.ndim == 1:
        data = data[:, np.newaxis]
    if S.ndim == 1:
        S = S[:, np.newaxis]

    if np.any(S < 0):
        print('NEGATIVE VARCOPES!!')

    p = mp.Pool(nprocesses)

    args = [(data[:, ii], design_matrix, S[:, ii], contrasts) for ii in range(data.shape[1])]

    res = p.starmap(_run_flame1, args, total=len(args))

    p.close()

    betas = np.vstack([r[0] for r in res])
    copes = np.vstack([r[1] for r in res])
    varcopes = np.vstack([r[2] for r in res])

    return betas, copes, varcopes


def compute_cookDistance(design_matrix, data):
    """Computes Cook distances for a given design matrix and corresponding data.

        Parameters
        ----------

        design_matrix :
            A [N x P] design matrix of regressors.

        data :
            A [N x M] vector of datapoints being analysed.

        Returns
        -------

        ndarray
            Array containing cook distances for each data sample.

        """

    [nsamples, ndim] = np.shape(design_matrix)
    [nsamplesdata, ndimdata] = np.shape(data)

    preds_full = np.matmul(design_matrix, np.matmul(np.linalg.pinv(design_matrix), data))
    resid_full = data - preds_full
    #s_sq = np.matmul(np.transpose(resid_full), resid_full) * 1 / (nsamples - ndim)
    s_sq = np.einsum('ij,ji->i', resid_full.T, resid_full) * (1 / (nsamples - ndim))

    cookdist = np.zeros([nsamples, ndimdata])
    for i in range(nsamples):
        print(i)
        DMi = np.delete(design_matrix, i, 0)
        Yi = np.delete(data, i, 0)
        Bi = np.matmul(np.linalg.pinv(DMi), Yi)
        pred_i = np.matmul(design_matrix, Bi)
        sumsq = np.sum(np.square(preds_full - pred_i), axis=0)
        cookdist[i, :] = sumsq / (s_sq * ndim)

    return cookdist
