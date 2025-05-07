#!/usr/bin/python

import yaml
import warnings
import numpy as np
from . import viz, regressors, util, fit, data
from anamnesis import AbstractAnam, register_class


# Contrast Class
class Contrast(AbstractAnam):

    hdf5_outputs = ['ctype', 'name', 'values']

    def __str__(self):
        return "%s(%s,%s)" % (self.__class__, self.name, self.ctype)

    def __init__(self, values=None, name=None):
        """Define a contrast for use on GLM parameters

        Parameters
        ----------
        values : array_like (1-dimensional)
            Values to defining contrast

        name : string (optional)
            Identifing label for contrast

        Returns
        -------
        Contrast instance

        """
        AbstractAnam.__init__(self)

        if values is not None:
            if isinstance(values, list):
                values = np.array(values)

            self.values = values
            if isinstance(self.values, dict):
                vals = np.array(self.values.values())
            else:
                vals = np.array(values)

            if vals.ndim > 1:
                raise ValueError('Invalid contrast shape {0} passed. Regressor must be 1d'.format(vals.shape))

            if vals.sum() == 0:
                self.ctype = 'Differential'
            else:
                self.ctype = 'MainEffect'

        if name is None:
            self.name = 'Contrast'
        else:
            self.name = name


register_class(Contrast)

# FTest Class


class FTest(AbstractAnam):

    hdf5_attrs = ['ctype', 'name', 'values']

    def __str__(self):
        return "%s(%s,%s)" % (self.__class__, self.name, self.ctype)

    def __init__(self, values=None, name=None):
        """Define a F-Test for use on GLM parameters

        Parameters
        ----------
        values : array_like (1-dimensional)
            Values to defining contrast

        name : string (optional)
            Identifing label for contrast

        Returns
        -------
        FTest instance

        """
        AbstractAnam.__init__(self)

        if values is not None:
            if isinstance(values, list):
                values = np.array(values)

            if values.ndim > 1:
                raise ValueError('Invalid f-test shape {0} passed. Regressor must be 1d'.format(values.shape))

            self.values = values
            self.ctype = 'FTest'

        if name is None:
            self.name = 'FTest'
        else:
            self.name = name


register_class(FTest)

# Design Class


class GLMDesign(AbstractAnam):
    """
    Class holding a glm design matrix and meta information
    """

    hdf5_outputs = ['design_matrix', 'contrasts', 'ftests',
                    'regressor_names', 'contrast_names', 'ftest_names',
                    'regressor_list', 'contrast_list', 'ftest_list',
                    ]

    def __init__(self):
        AbstractAnam.__init__(self)

    @property
    def num_observations(self):
        "The number of observations in the design matrix (length of the first dimension)"
        return self.design_matrix.shape[0]

    @property
    def num_regressors(self):
        "The number of regressors in the design matrix (length of the second dimension)"
        return self.design_matrix.shape[1]

    @property
    def num_contrasts(self):
        "The number of contrasts in the contrast matrix (length of the first dimension)"
        return self.contrasts.shape[0]

    @property
    def num_ftests(self):
        "The number of f-tests in the f matrix (length of the first dimension)"
        if self.ftests is None:
            return 0
        else:
            return self.ftests.shape[0]

    @property
    def design_matrix_rank(self):
        "The number of linearly independent regressors in the design matrix"
        return np.linalg.matrix_rank(self.design_matrix)

    @property
    def dof_error(self):
        "The model degrees of freedom (num observations - num regressors)"
        return self.num_observations - self.design_matrix_rank

    @property
    def leverage(self):
        return np.diag(self.design_matrix.dot(np.linalg.pinv(self.design_matrix)))

    # Visualisations
    def print_summary(self):
        "Print a text summary of the model."

        viz.print_contrast_table(self.contrasts,
                                 contrast_names=self.contrast_names,
                                 regressor_names=self.regressor_names,
                                 f_tests=self.ftest_list,
                                 ftest_names=self.ftest_names)

    def summarise_design(self):
        print('\n')
        print(viz.summarise_regressor_list(self.regressor_list))
        print('\n')
        print(viz.summarise_contrasts(self.contrasts, self.contrast_names, self.regressor_names))

    def plot_efficiency(self, show=True, savepath=None):
        "Plot the correlation matrix and singular values from the design matrix"

        fig = viz.plot_design_efficiency(self.design_matrix,
                                         regressor_names=self.regressor_names,
                                         normalise_singlar_values=True)

        import matplotlib.pyplot as plt
        if savepath is not None:
            plt.savefig(savepath, dpi=300)

        if show:
            plt.show()
        else:
            plt.close(fig)

        return fig

    def plot_summary(self, show=True, savepath=None, summary_lines=True,
                     fig=None, ax=None, figargs=dict()):
        "Plot a summary of the design matrix and contrasts"

        fig = viz.plot_design_summary(self.design_matrix,
                                      self.regressor_names,
                                      contrasts=self.contrasts,
                                      contrast_names=self.contrast_names,
                                      ftests=self.ftests,
                                      ftest_names=self.ftest_names,
                                      summary_lines=summary_lines,
                                      fig=fig, ax=ax, figargs=figargs)

        import matplotlib.pyplot as plt
        if savepath is not None:
            plt.savefig(savepath, dpi=300)

        if show:
            plt.show()
        else:
            plt.close(fig)

        return fig

    def plot_leverage(self, thresh=5, show=True, savepath=None):
        """Plot a summary of the leverage across observations in the design matrix"""

        fig = viz.plot_leverage(self.leverage, thresh=thresh)

        import matplotlib.pyplot as plt
        if savepath is not None:
            plt.savefig(savepath, dpi=300)

        if show:
            plt.show()
        else:
            plt.close(fig)

        return fig

    def sanity_check(self, corr_check=False):
        """
        Run some checks to make sure nothing daft is happening
        """

        if self.design_matrix.shape[1] != self.contrasts.shape[1]:
            raise ValueError('Number of predictors in design matrix [%s] and contrasts [%s] do not match'
                             % (self.design_matrix.shape[1], self.contrasts.shape[1]))

        # Check names are correct length
        if self.num_regressors != len(self.regressor_names):
            raise ValueError('Number of regressors defined [%s] and number of regressor labels [%s] do no match'
                             % (self.num_regressors, len(self.regressor_names)))
        if self.num_contrasts != len(self.contrast_names):
            raise ValueError('Number of contrasts defined [%s] and number of contrast labels [%s] do no match'
                             % (self.num_contrasts, len(self.contrast_names)))
        if self.num_regressors != len(self.regressor_names):
            raise ValueError('Number of regressors defined [%s] and number of regressor labels [%s] do no match'
                             % (self.num_regressors, len(self.regressor_names)))
        if self.ftests is not None:
            if self.num_ftests != len(self.ftest_names):
                raise ValueError('Number of f_tests defined [%s] and number of f_test labels [%s] do no match'
                                 % (self.num_ftests, len(self.ftest_names)))

        if corr_check:
            # Constant regressors will lead to an invalid value in divide error, we
            # will ignore this
            old_settings = np.seterr(all='ignore')  # seterr to known value
            np.seterr(divide='ignore')

            if self.num_regressors > 1:
                c = np.corrcoef(self.design_matrix.T)
                c = c - np.diag(np.diag(c))
                if np.any(np.abs(c) > .95):
                    inds = np.where(np.abs(c).max(axis=0) > .95)[0]
                    warnings.warn('Highly correlated regressors found. inds=({0})'.format(inds))
            np.seterr(**old_settings)  # reset to default

    @classmethod
    def initialise(cls, regressors, contrasts, ftests=None):
        """Define a GLM design from a set of regressor and contrast objects

        Parameters
        ----------
        regressors : typed list (list of *Regressor objects)
            List of Regressor objects

        contrasts : typed list (list of Contrast objects)
            List of Contrast objects

        Returns
        -------
        Contrast instance

        """

        if len(set([len(a.values) for a in regressors])) > 1:
            raise ValueError('Regressor lengths are mismatched')

        if len(set([len(a.values) for a in contrasts])) > 1:
            raise ValueError('Contrast lengths are mismatched')

        if len(contrasts[0].values) != len(regressors):
            msg = 'Contrast lengths do not match number of regressors ( {0} and {0} )'
            raise ValueError(msg.format(len(contrasts[0].values), len(regressors)))

        ret = cls()

        ret.design_matrix = np.array([x.values for x in regressors]).T
        ret.regressor_names = [x.name for x in regressors]
        ret.contrasts = np.array([x.values for x in contrasts])
        ret.contrast_names = [x.name for x in contrasts]

        if ftests is not None:
            ret.ftests = np.array([x.values for x in ftests])
            ret.ftest_names = [x.name for x in ftests]
        else:
            ret.ftests = None
            ret.ftest_names = None

        ret.regressor_list = regressors
        ret.contrast_list = contrasts
        ret.ftest_list = ftests

        return ret

    @classmethod
    def initialise_from_matrices(cls, design_matrix, contrasts, ftests=None,
                                 regressor_names=None, contrast_names=None, ftest_names=None):
        """
        Initialise class with GLM info and precompute some useful values
        """

        ret = cls()
        ret.design_matrix = design_matrix
        ret.contrasts = contrasts

        # Set default regressor names if not provided
        if regressor_names is None:
            ret.regressor_names = np.arange(ret.design_matrix.shape[1]).astype(str)
        else:
            ret.regressor_names = regressor_names
        ret.regressor_list = []

        # Set default contrast names if not provided
        if contrast_names is None:
            ret.contrast_names = np.arange(ret.design_matrix.shape[1]).astype(str)
        else:
            ret.contrast_names = contrast_names

        # Define any F tests
        if ftests is not None:
            ret.ftests = ftests
            if ftest_names is None:
                # Use default names if they aren't provided
                ret.ftest_names = np.arange(ret.ftests.shape[1]).astype(str)
            else:
                ret.ftest_names = ftest_names
        else:
            ret.ftests = None
            ret.ftest_names = None

        ret.sanity_check()

        return ret


register_class(GLMDesign)


def variance_inflation_factor(design_matrix, return_betas=False):
    """Compute variance inflation factor of each regressor.

    https://en.wikipedia.org/wiki/Variance_inflation_factor
    """

    num_regressors = design_matrix.shape[1]

    contrasts = np.zeros((1, num_regressors-1))
    contrast_names = ['A']

    vif = np.zeros((num_regressors,))
    betas = np.zeros((num_regressors, num_regressors)) * np.nan

    for ind in range(num_regressors):
        y = data.TrialGLMData(data=design_matrix[:, ind])
        X = np.delete(design_matrix.copy(), ind, axis=1)

        regressor_names = [str(64 + ii) for ii in range(num_regressors-1)]
        D = GLMDesign.initialise_from_matrices(X, contrasts,
                                               contrast_names=contrast_names,
                                               regressor_names=regressor_names)

        model = fit.OLSModel(D, y)
        betas[np.setdiff1d(np.arange(num_regressors), ind), ind] = model.betas[:, 0]

        vif[ind] = 1 / (1-model.r_square[0, 0])

    if return_betas:
        return vif, betas
    else:
        return vif


class RegressorList(list):

    def add(self, rtype, **kwargs):

        if rtype.find('Regressor') == -1:
            # Input is short regressor class name
            rtype += 'Regressor'

        r = getattr(regressors, rtype)

        if r is None:
            raise ValueError('Regressor type {0} not recognised'.format(rtype))

        self.append(r(**kwargs))


class DesignConfig:

    def __init__(self, yaml_text=None):
        if yaml_text is None:
            self.name = 'NewDesign'
            self.regressors = list()
            self.contrasts = list()
            self.ftests = list()
        else:
            import yaml
            conf = yaml.load(yaml_text, Loader=yaml.FullLoader)
            self.name = list(conf.keys())[0]

            self.regressors = list()
            self.contrasts = list()
            self.ftests = list()

            for reg in conf[self.name]['regressors']:
                self.add_regressor(**reg)

            for con in conf[self.name]['contrasts']:
                self.add_contrast(**con)

            if 'ftest' in conf[self.name]:
                for ft in conf[self.name]['f_tests']:
                    self.add_ftest(**ft)
            else:
                self.ftest = None

            for con in self.contrasts:
                if isinstance(con['values'], str):
                    v = list(map(float, con['values'].split()))
                    con['values'] = v

    @property
    def num_regressors(self):
        return len(self.regressors)

    @property
    def num_contrasts(self):
        return len(self.contrasts)

    @property
    def regressor_names(self):
        return [r['name'] for r in self.regressors]

    @property
    def contrast_names(self):
        return [c['name'] for c in self.contrasts]

    def add_regressor(self, rtype, **kwargs):

        if rtype.find('Regressor') == -1:
            # Input is short regressor class name
            rtype += 'Regressor'
        kwargs['regressor'] = rtype

        if 'name' not in kwargs:
            kwargs['name'] = 'Regressor{0}'.format(self.regressors.__len__())

        # Add new regressor and update contrasts
        self.regressors.append(kwargs)

        # Append to existing contrasts
        for c in self.contrasts:
            if not isinstance(c['values'], dict):
                c['values'].append(0)

    def add_contrast(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = 'Regressor{0}'.format(self.regressors.__len__())
        if isinstance(kwargs['values'], str):
            kwargs['values'] = list(map(float, kwargs['values'].split(' ')))
        elif isinstance(kwargs['values'], list):
            kwargs['values'] = list(map(float, kwargs['values']))
        self.contrasts.append(kwargs)

    def add_ftest(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = 'Contrast{0}'.format(self.contrasts.__len__())
        if isinstance(kwargs['values'], str):
            kwargs['values'] = list(map(float, kwargs['values'].split(' ')))
        elif isinstance(kwargs['values'], list):
            kwargs['values'] = list(map(float, kwargs['values']))
        self.ftests.append(kwargs)

    def _check_regressor(self, reg):

        isgood = True  # Start positive
        rtype = reg['regressor']
        try:
            if rtype.find('Regressor') == -1:
                # Input is short regressor class name
                rtype += 'Regressor'

            if rtype == 'MeanEffectsRegressor':
                pass
            else:
                getattr(regressors, rtype)
        except AttributeError:
            print('Regressor: {0} - not recognised'.format(rtype))
            isgood = False
        return isgood

    def _check_contrast(self, con):
        isgood = True  # Start positive
        if isinstance(con['values'], dict):
            for key in con['values']:
                if key not in self.regressor_names:
                    print("Contrast: {0} - regressor name ({1}) not found".format(con['name'], key))
        else:
            if len(con['values']) != self.num_regressors:
                print('Contrast: {0} - values mis-matched to num_regressors'.format(con['name']))
            isgood = False
        return isgood

    def _check_ftest(self, ft):
        isgood = True  # Start positive
        if isinstance(ft['values'], dict):
            for key in ft['values']:
                if key not in self.contrast_names:
                    print("F-Test: {0} - contrast name ({1}) not found".format(ft['name'], key))
        else:
            if len(ft['values']) != self.num_regressors:
                print('F-Test: {0} - values mis-matched to num_contrasts'.format(ft['name']))
            isgood = False
        #if len(ft['values']) != self.num_contrasts:
        #    print('F-test: {0} - values mis-matched to num_contrasts'.format(ft['name']))
        #    isgood = False
        return isgood

    def add_simple_contrasts(self, reg_names=None):

        if reg_names is None:
            reg_names = self.regressor_names

        for reg in reg_names:
            for ind, r in enumerate(self.regressors):
                if r['name'] == reg:
                    #values = list(np.zeros((self.num_regressors,)))
                    #values[ind] = 1
                    values = {r['name']: 1}
                    self.add_contrast(name=r['name'], values=values)

    def add_mean_effects(self, groups, basename='Mean{0}'):

        for g in np.unique(groups):
            self.add_regressor('Categorical',
                               category_list=groups,
                               codes=g,
                               name=basename.format(g))

    def to_dict(self):
        self.validate()
        # Export to yaml text
        dd = {'regressors': self.regressors, 'contrasts': self.contrasts}
        conf = {self.name: dd}
        return conf

    def to_yaml(self):
        self.validate()
        conf = self.to_dict()
        return yaml.dump(conf, default_flow_style=None, explicit_start=True, width=1000)

    def to_yaml_file(self, fname):
        """Save a copy of the internal store in a specified yaml file."""
        self.validate()
        conf = self.to_dict()
        with open(fname, 'w') as f:
            return yaml.dump(conf, f, default_flow_style=None, explicit_start=True, width=1000)

    @classmethod
    def from_yaml_file(cls, fname):
        """Create and return a new DesignConfig object with options loaded from a yaml file."""
        with open(fname, 'r') as f:
            cfg = [d for d in yaml.load_all(f, Loader=yaml.FullLoader)]
            if len(cfg) == 1:
                ret = cls().from_dict(cfg[0])
            else:
                raise RuntimeError('Multiple configs found in file')

        return ret

    @classmethod
    def from_dict(cls, indict):
        ret = cls()
        ret.name = list(indict.keys())[0]
        ret.regressors = indict[ret.name]['regressors']
        ret.contrasts = indict[ret.name]['contrasts']
        ret.validate()
        return ret

    def validate(self):

        r = np.all([self._check_regressor(reg) for reg in self.regressors])
        c = np.all([self._check_contrast(con) for con in self.contrasts])

        if self.ftests is not None:
            f = np.all([self._check_ftest(ft) for ft in self.ftests])
        else:
            f = True

        return (r, c, f)

    def design_from_datainfo(self, info):
        self.validate()

        regressors = util.regressors_from_datainfo(self.regressors, info)
        contrasts = util.contrasts_from_dict(self.contrasts, regs=regressors)
        if self.ftests is not None:
            ftests = util.ftests_from_dict(self.ftests, regs=contrasts)
        else:
            ftests = None

        return GLMDesign.initialise(regressors, contrasts, ftests)
