#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import numpy as np
from copy import deepcopy
from . import util, design, regressors
from .viz import plot_outliers
from anamnesis import AbstractAnam, register_class

# Abstract Class
# --------------


class AbstractGLMData(AbstractAnam):
    """
    Abstract class defining some routines for the GLM Data classes.
    """

    hdf5_outputs = ['data', 'info']

    @property
    def orig_shape(self):
        "The shape of the original data"
        return self.data.shape

    @property
    def squash_shape(self):
        "The shape of the data after reshaping before model fitting."
        return (self.data.shape[0], np.prod(self.data.shape[1:]))

    @property
    def num_observations(self):
        "The number of observations in the data, this is the first dimension of the input data"
        return self.data.shape[0]

    @classmethod
    def initialise(cls):
        raise NotImplementedError('This is an abstract class, please use TrialGLMData or ContinuousGLMData')

    def get_2d_data(self):
        """Method which reshapes the data in preparation for model fitting.

        The model fitting runs over the first dimension of the input data, any
        other dimensions are concatenated to create a 2d matrix which greatly
        speeds up computation.

        Returns
        -------
        2d array
            The reshaped dataset

        """

        return self.data.reshape(self.squash_shape)

    def unsquash_array(self, X):
        """Method for reversing the data reshaping prior to model fitting.

        The model fit runs on a d2 version of the data, this method reverses
        this reshaping on an arbitrary 2d matrix to create an array whose
        second to final dimensions match that of the input data.

        Parameters
        ----------

        X : 2d array
            Array of data to reshape. The first dimension length is arbitrary,
            the second must be equivalent to the product of the second:last
            dimensions of the data defined in the parent object.

        Returns
        -------
        ndarray
            Reshaped data array

        """

        new_shape = tuple((X.shape[0], *self.orig_shape[1:]))
        return X.reshape(*new_shape)

    def drop(self, inds, inplace=False):

        if inplace is False:
            ret = deepcopy(self)
        else:
            # Just a pointer
            ret = self

        for key in ret.info.keys():
            if isinstance(ret.info[key], (list, np.ndarray)) and len(ret.info[key]) == ret.data.shape[0]:
                ret.info[key] = np.delete(np.array(ret.info[key]), inds)

        ret.data = np.delete(ret.data, inds, axis=0)
        ret.info['num_observations'] = ret.data.shape[0]

        return ret

    def plot_outliers(self, thresh=5):
        return plot_outliers(self.data, thresh=thresh)


class TrialGLMData(AbstractGLMData):
    """
    Class holding data intended for GLM modelling across trials.
    """

    def __init__(self, **kwargs):
        """Constructor method for GLM dataset object.

        Parameters
        ----------

        data : ndarray
            Array of observed data. First dimension must refer to trials, the
            rest are arbitrary.

        category_list : 1d array_like (optional)
            array or list of labels indicating trial types

        time_dim : int
            Index of dimension containing time

        Returns
        -------
        TrialGLMData object instance

        """
        AbstractAnam.__init__(self)

        # Store data if passed in
        if 'data' in kwargs:
            self.data = kwargs['data']
            # Make sure data is at least 2d
            if np.ndim(self.data) == 1:
                self.data = self.data[:, None]
            del kwargs['data']
        else:
            self.data = None

        self.info = {}
        if len(kwargs) > 0:

            for key, value in kwargs.items():
                self.info[key] = value

        if (self.data is not None):

            # Make sure that the data and condition definitions match shape
            if self.data is not None and 'category_list' in self.info:
                if self.data.shape[0] != self.info['category_list'].shape[0]:
                    raise ValueError('Number of observations in data [%s] condition list [%s] do no match'
                                     % (self.data.shape[0],
                                        self.info['category_list'][0]))

            # Set condition list if not defined
            if 'category_list' not in self.info:
                self.info['category_list'] = np.ones((self.data.shape[0], ))

            # Set default dimension labels if not defined
            if self.data is not None and 'dim_labels' not in self.info:
                self.info['dim_labels'] = list(('Trials', *['dim'+chr(65+ii)
                                                            for ii in range(self.data.ndim-1)]))

            if 'num_observations' not in self.info:
                self.info['num_observations'] = self.data.shape[0]

    def save(self, fname):
        import pickle
        with open(fname, 'wb') as f:
            pickle.dump(self, f)

    @property
    def conditions(self):
        "Return the unique condition labels in this dataset"
        return np.unique(self.info['category_list'])

    def get_condition_counts(self):
        "Return the number of occurances of each trial type"
        return [sum(self.info['category_list'] == x) for x in self.conditions]

    def get_condition_inds(self, conditions):
        """
        Return the indices for occurances of defined trial-types

        :param conditions - tuple containing condition values eg (1,2,5)

        :returns: boolean index to matching trials

        """

        return np.sum(self.info['condition_list'] == conditions, axis=1)

    def get_simple_regressors(self, condition_groups, condition_group_names=None, add_constant=True, standardise=None):
        """Create a list of Regressor objects based on the conditions and
        trials present in this dataset.

        Parameters
        ----------

        condition_groups : list of tuples
            List of condition labels defining groups of trial types. Each
            element in the list contains a tuple of n trial labels
            eg [ (1,2),(3,4) ]

        condition_group_names : list of strings (optional)
            Identifying labels for the condition groups.

        add_constant : boolean (default=True)
            Flag indicating whether to include a constant regressor

        standardise : boolean (default=True)
            Flag indicating whether to z-transform non-constant regressors

        Returns
        -------

        list of Regressor objects

        """

        regressors = list()

        if add_constant:
            regressors.append(design.ConstantRegressor(self.num_observations, name='Constant'))

        if condition_group_names is None:
            condition_group_names = [str(65+ii) for ii in range(len(condition_groups))]

        for ii in range(len(condition_groups)):
            regressors.append(design.ConditionRegressor(conditions=self.condition_list,
                                                        trial_codes=condition_groups[ii],
                                                        name=condition_group_names[ii],
                                                        preproc=standardise))

        return regressors


register_class(TrialGLMData)


class ContinuousGLMData(AbstractGLMData):
    """
    Class holding a dataset intended for GLM modelling
    """

    def __init__(self, **kwargs):
        """
        Constructor method for GLM dataset object.

        :param data: matrix of observed data. First dimension must refer to time, the rest are arbitrary.
        :param sample_rate: float indicating sampling frequency
        :param start_time: float indicating the absolute time of the first sample

        :returns: ContinuousGLMData object instance

        """
        AbstractAnam.__init__(self)

        # Store data if passed in
        if 'data' in kwargs:
            self.data = kwargs['data']
            # Make sure data is at least 2d
            if np.ndim(self.data) == 1:
                self.data = self.data[:, None]
            del kwargs['data']
        else:
            self.data = None

        self.info = {}
        self.info['time_dim'] = 0

        if len(kwargs) > 0:

            for key, value in kwargs.items():
                self.info[key] = value

            if 'dim_labels' not in kwargs:
                print('new dim_labels')
                self.info['dim_labels'] = list(('Time', *['dim'+chr(65+ii) for ii in
                                                          range(self.data.ndim-1)]))

            if 'start_time' not in kwargs:
                self.start_time = 0

    @property
    def time_vect(self):
        end_time = (self.sample_rate / self.num_observations) - self.start_time
        return np.linspace(self.start_time, end_time, self.num_observations)


register_class(ContinuousGLMData)


class HigherLevelData(AbstractGLMData):
    """
    A Class for grouping fitted General Linear Models
    """

    hdf5_outputs = ['copes', 'varcopes', 'coapes', 'betas', 'models',
                    'first_level_regressor_names',
                    'first_level_contrast_names',
                    'beta_dimlabels', 'cope_dimlabels', 'tstat_dimlabels',
                    'first_level_stat']

    def __init__(self, models=None, group_conf=None, datasets=None, first_level_stat='tstats'):
        """Define a Model Group from a list of GLMFit instances.

        Parameters
        ----------

        models : list of GLMFit instances.
            List of GLM fits to merge into a group. The shape of GLM estimate
            arrays (betas,copes etc) must match across models

        group_conf : dict
            Definition of the group structure as parsed from a yaml file

        Returns
        -------

        ModelGroup instance

        """
        AbstractAnam.__init__(self)

        if models is None:
            self.beta_dimlabels = tuple([])
            self.cope_dimlabels = tuple([])
            self.tstat_dimlabels = tuple([])
            self._first_level_stat = 'copes'
            self.info = {'dim_labels': self.dim_labels}
            return

        s = [s.copes.shape for s in models]
        if len(set(s)) > 1:
            counts = [sum(s == x) for x in np.unique(s)]
            print(np.unique(s))
            print(counts)
            raise ValueError('A dataset is mismatched')

        self.models = models
        self._first_level_stat = first_level_stat
        self._first_level_varcope_smoothing = None

        # These return empty if no models are passed in allowing for empty initialisation in classmethods
        self.betas = np.array([o.betas for o in models])
        self.copes = np.array([o.copes for o in models])
        self.varcopes = np.array([o.varcopes for o in models])
        self.coapes = np.array([o.coapes for o in models])
        self.fstats = np.array([o.fstats for o in models])

        if len(models) > 0:
            self.first_level_regressor_names = models[0].regressor_names
            self.first_level_contrast_names = models[0].contrast_names
            self.first_level_ftest_names = models[0].ftest_names
            self.time_dim = models[0].time_dim
            self.beta_dimlabels = tuple(('LowerLevels', *models[0].beta_dimlabels))
            self.cope_dimlabels = tuple(('LowerLevels', *models[0].cope_dimlabels))
            self.tstat_dimlabels = tuple(('LowerLevels', *models[0].cope_dimlabels))

        # TODO: parse this properly into tag compatable info
        self.info = {}
        if datasets is not None:
            for key in datasets[0].keys():
                self.info[key] = [d[key] for d in datasets]
            self.info['num_observations'] = len(datasets)
            self.info['dim_labels'] = self.dim_labels

    @property
    def data(self):
        if self.first_level_stat == 'tstats':
            return self.get_tstats(temporal_varcope_smoothing=self.first_level_varcope_smoothing)
        else:
            return getattr(self, self.first_level_stat)

    @property
    def first_level_varcope_smoothing(self):
        return self._first_level_varcope_smoothing

    @first_level_varcope_smoothing.setter
    def first_level_varcope_smoothing(self, value):
        self._first_level_varcope_smoothing = value

    @property
    def first_level_stat(self):
        return self._first_level_stat

    @property
    def dim_labels(self):
        return getattr(self, self._first_level_stat[:-1] + '_dimlabels')

    @first_level_stat.setter
    def first_level_stat(self, value):

        if value not in ['copes', 'tstats', 'fstats']:
            raise ValueError('first_level_stat {0} not recognised. Please use \'copes\', \'tstats\' or \'fstats\'')
        self._first_level_stat = value
        self.info['dim_labels'] = self.dim_labels

    def get_tstats(self, temporal_varcope_smoothing=None, smoothing_window=np.hanning, smooth_dims=None):
        """Computes t-statistics from COPEs in a fitted model, may add optional
        temporal varcope smoothing. Calls get_stats() method on the underlying
        GLMFit instances.

        Parameters
        ----------

        temporal_varcope_smoothing : {None, int} (optional, default=None)
            Optional window length for varcope smoothing of time dimension. The
            default is no smoothing as indicated by None.

        smoothing_window : {np.hanning,np.bartlett,np.blackman,np.hamming} default=np.hanning
            One of numpys window functions to apply during smoothing. Ignored
            if temporal_varcope_smoothing=None

        Returns
        -------

        ndarray
            Array containing t-statistic estimates

        """

        return util.compute_t_stats(self.copes, self.varcopes,
                                    temporal_varcope_smoothing=temporal_varcope_smoothing,
                                    smoothing_window=smoothing_window,
                                    smooth_dims=smooth_dims)

    def get_simple_regressors(self, dummy_code=None, contrast=None, parametric=None):

        reg = list()

        if dummy_code is not None:
            # List of lists containing category allocations
            dummies = [self.info[a] for a in dummy_code]

            # List of tuples containing relevant categories
            import itertools
            dummies_merged = list(itertools.zip_longest(*dummies))

            # Get unique tuples and indices of their location
            uni, uni_inds = np.unique(dummies_merged, axis=0, return_inverse=True)

            # Create regressors
            for ii in range(len(uni)):
                name = ''
                for jj in range(len(dummy_code)):
                    name += dummy_code[jj] + str(uni[ii])
                reg.append(regressors.CategoricalRegressor(name=name, category_list=uni_inds, codes=ii, **self.info))

        if contrast is not None:
            # Not so happy with this
            for ii in range(len(contrast)):
                reg.append(regressors.CategoricalRegressor(name=contrast[ii],
                                                           category_list=self.info[contrast[ii]],
                                                           codes=self.info[contrast[ii]][0],
                                                           **self.info))

        if parametric is not None:
            for ii in range(len(parametric)):
                name = parametric[ii]
                reg.append(regressors.ParametricRegressor(name=name,
                                                          values=self.info[parametric[ii]],
                                                          preproc='z',
                                                          **self.info))

        return reg


register_class(HigherLevelData)
