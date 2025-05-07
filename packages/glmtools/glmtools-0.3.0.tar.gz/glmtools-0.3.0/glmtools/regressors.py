#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import numpy as np
from anamnesis import AbstractAnam, register_class

# Regressor Classes

# This abstract contains the normalisation routines that might be used in
# children


class AbstractRegressor(AbstractAnam):
    """
    Class holding a glm design matrix and meta information
    """

    def __str__(self):
        return "%s(%s,%s)" % (self.__class__, self.name, self.rtype)

    hdf5_outputs = ['rtype', 'values', 'name', 'values_orig']

    def __init__(self, **kwargs):
        AbstractAnam.__init__(self)

        self.rtype = None
        self.values = None
        self.values_orig = None
        self.name = None

    def parse_arguments(self, kwargs):
        raise NotImplementedError('This is an AbtractClass')

    def normalise_values(self):

        self.values_orig = self.values.copy()

        if self.preproc == 'z':
            self.values = (self.values - self.values.mean()) / self.values.std()
        elif self.preproc == 'demean':
            self.values = self.values - self.values.mean()
        elif self.preproc == 'unitmax':
            self.values = self.values / self.values.max()
        else:
            self.values = self.values


class ConstantRegressor(AbstractRegressor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        AbstractAnam.__init__(self)

        self.rtype = 'Constant'

        if len(kwargs) > 0:
            self.parse_arguments(kwargs)

            self.values = np.ones((self.num_observations, ))*self.magnitude
        else:
            self.values = None
            self.name = 'Unknown'

    def parse_arguments(self, extraargs):
        """
        num_observations
        magnitude
        """

        if 'num_observations' in extraargs:
            self.num_observations = extraargs['num_observations']
        else:
            raise ValueError('num_observations not passed to ConditionRegressor')

        if 'magnitude' in extraargs:
            self.magnitude = extraargs['magnitude']
        else:
            self.magnitude = 1

        if 'name' in extraargs:
            self.name = extraargs['name']
        else:
            self.name = 'Constant'


register_class(ConstantRegressor)


class TrendRegressor(AbstractRegressor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        AbstractAnam.__init__(self)

        self.rtype = 'Trend'

        if len(kwargs) > 0:
            self.parse_arguments(kwargs)

            self.values = np.power(np.linspace(0, 1, self.num_observations), self.power)
            self.normalise_values()
        else:
            self.values = None
            self.name = 'Unknown'

    def parse_arguments(self, extraargs):
        """
        num_observations
        power
        preproc
        """

        if 'num_observations' in extraargs:
            self.num_observations = extraargs['num_observations']
        else:
            raise ValueError('num_observations not passed to ConditionRegressor')

        if 'power' in extraargs:
            self.power = extraargs['power']
        else:
            # Default is a linear trend
            self.power = 1

        if 'name' in extraargs:
            self.name = extraargs['name']
        else:
            self.name = 'Condition'

        if 'preproc' in extraargs:
            self.preproc = extraargs['preproc']
        else:
            # Default to unit maximum normalisation
            self.preproc = 'unitmax'


register_class(TrendRegressor)


class SineRegressor(AbstractRegressor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        AbstractAnam.__init__(self)

        self.rtype = 'Sine'

        if len(kwargs) > 0:
            self.parse_arguments(kwargs)

            t = np.linspace(0, 1, self.num_observations)
            self.values = np.sin(2*np.pi*self.freq*t + self.phase)
            self.normalise_values()
        else:
            self.values = None
            self.name = 'Unknown'

    def parse_arguments(self, extraargs):
        """
        num_observations
        power
        preproc
        """

        if 'num_observations' in extraargs:
            self.num_observations = extraargs['num_observations']
        else:
            raise ValueError('num_observations not passed to ConditionRegressor')

        if 'freq' in extraargs:
            self.freq = extraargs['freq']
        else:
            # Default is a linear trend
            self.freq = 1

        if 'phase' in extraargs:
            self.phase = extraargs['phase']
        else:
            # Default is a linear trend
            self.phase = 0

        if 'name' in extraargs:
            self.name = extraargs['name']
        else:
            self.name = 'Condition'

        if 'preproc' in extraargs:
            self.preproc = extraargs['preproc']
        else:
            # Default to unit maximum normalisation
            self.preproc = 'unitmax'


register_class(SineRegressor)


class CategoricalRegressor(AbstractRegressor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        AbstractAnam.__init__(self)

        self.rtype = 'Categorical'

        if len(kwargs) > 0:
            self.parse_arguments(kwargs)

            self.values = np.sum(self.category_list == self.codes, axis=1)
            self.normalise_values()
        else:
            self.values = None
            self.name = 'Unknown'

    def parse_arguments(self, extraargs):
        """
        category_list array_like - cast to [n,1]
        codes tuple
        name
        preproc
        """

        if 'datainfo' in extraargs:
            self.category_list = np.array(extraargs[extraargs['datainfo']])
        elif 'category_list' in extraargs:
            self.category_list = np.array(extraargs['category_list'])
        else:
            raise ValueError('category_list not passed to ConditionRegressor')

        # Sanity checks
        # Ensure we have a [nobs x 1] numpy array so the element-wise comparison will work
        if self.category_list.ndim == 1:
            self.category_list = self.category_list[:, None]
        if self.category_list.shape[1] != 1:
            raise ValueError('category_list must be either 1d-array_like or [nobservations x 1] array_like')

        if 'codes' in extraargs:
            self.codes = extraargs['codes']

            # Ensure codes is an int array with singleton second dimension
            if isinstance(self.codes, str):
                self.codes = (np.array(self.codes.split(' ')).astype(float))
        else:
            raise ValueError('codes not passed to ConditionRegressor')

        if 'name' in extraargs:
            self.name = extraargs['name']
        else:
            self.name = 'Condition'

        if 'preproc' in extraargs:
            self.preproc = extraargs['preproc']
        else:
            self.preproc = None


register_class(CategoricalRegressor)


class ParametricRegressor(AbstractRegressor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        AbstractAnam.__init__(self)

        self.rtype = 'Parametric'

        if len(kwargs) > 0:
            self.parse_arguments(kwargs)
            self.values = np.power(self.values, self.power)
            self.normalise_values()
        else:
            self.values = None
            self.name = 'Unknown'

    def parse_arguments(self, extraargs):
        """
        values
        preproc
        """

        if 'values' in extraargs:
            self.values = np.array(extraargs['values'])
        elif 'datainfo' in extraargs:
            self.values = np.array(extraargs[extraargs['datainfo']])
        else:
            raise ValueError('values or datainfo not passed to ParametricRegressor class')

        if self.values.shape[0] != extraargs['num_observations']:
            msg = 'Regressor shape ({0}) and Data shape ({1}) do not match'
            raise ValueError(msg.format(self.values.shape, extraargs['num_observations']))

        if 'power' in extraargs:
            self.power = extraargs['power']
        else:
            # Default is a linear trend
            self.power = 1

        if 'preproc' in extraargs:
            self.preproc = extraargs['preproc']
        else:
            # Default is to z-transform values
            self.preproc = 'z'

        if 'name' in extraargs:
            self.name = extraargs['name']
        else:
            self.name = 'Parametric'


register_class(ParametricRegressor)


class InteractionRegressor(AbstractRegressor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        AbstractAnam.__init__(self)

        self.rtype = 'Interaction'

        if len(kwargs) > 0:
            self.parse_arguments(kwargs)
            self.normalise_values()
        else:
            self.values = None
            self.name = 'Unknown'

    def parse_arguments(self, extraargs):
        """
        values
        preproc
        """

        if 'regressors' in extraargs:
            vals = np.hstack([np.array(extraargs[key])[:, None] for key in extraargs['regressors']])
            self.values = np.prod(vals, axis=1)
        else:
            raise ValueError('"regressors" not passed to InteractionRegressor class')

        if self.values.shape[0] != extraargs['num_observations']:
            msg = 'Regressor shape ({0}) and Data shape ({1}) do not match'
            raise ValueError(msg.format(self.values.shape, extraargs['num_observations']))

        if 'preproc' in extraargs:
            self.preproc = extraargs['preproc']
        else:
            # Default is to z-transform values
            self.preproc = 'z'

        if 'name' in extraargs:
            self.name = extraargs['name']
        else:
            self.name = 'Interaction'


register_class(InteractionRegressor)


class BoxcarRegressor(AbstractRegressor):

    def __init__(self, *args, **kwargs):
        """Create a boxcar regressor

        Parameters
        ----------
        nsamples : int
            total length of regressor

        trls : list of tuples
            List of start and stop samples for 'on' sections of the boxcar
            e.g. [ (2,10),(20,30),(40,50]

        magnitude : float (optional)
            The height of the boxcar. Default value is 1

        name : string (optional)
            Identifing label for regressor

        Returns
        -------
        BoxcarRegressor instance

        """
        super().__init__(*args, **kwargs)
        AbstractAnam.__init__(self)

        self.rtype = 'Boxcar'

        if len(kwargs) > 0:
            self.parse_arguments(kwargs)

            self.values = np.zeros((self.num_observations,))
            inds = np.hstack([np.arange(x, y) for (x, y) in self.trls])
            self.values[inds] = self.magnitude
        else:
            self.values = None
            self.name = 'Unknown'

    def parse_arguments(self, extraargs):
        """
        num_observations
        trls
        magnitude
        name
        """

        if 'trls' in extraargs:
            self.trls = extraargs['trls']
        else:
            raise ValueError('trls not passed to BoxCarRegressor')

        if 'num_observations' in extraargs:
            self.num_observations = extraargs['num_observations']
        else:
            raise ValueError('num_observations not passed to ConditionRegressor')

        if 'magnitude' in extraargs:
            self.magnitude = extraargs['magnitude']
        else:
            # Default is one
            self.magnitude = 1

        if 'name' in extraargs:
            self.name = extraargs['name']
        else:
            self.name = 'Condition'


register_class(BoxcarRegressor)


class ConvolutionalRegressor(AbstractRegressor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        AbstractAnam.__init__(self)

        self.rtype = 'Convolutional'

        if len(kwargs) > 0:
            self.parse_arguments(kwargs)

            self.values = np.zeros((self.num_observations,))
            self.values[self.impulse_inds] = 1

            if self.basis == 'sine':
                self.basis = np.linspace(0, self.basis_len/self.sample_rate, self.basis_len)
                self.basis = np.sin(2*np.pi*self.frequency*self.basis)
            elif self.basis == 'cosine':
                self.basis = np.linspace(0, self.basis_len/self.sample_rate, self.basis_len)
                self.basis = np.cos(2*np.pi*self.frequency*self.basis)

            self.values = np.convolve(self.values, self.basis, 'same')
        else:
            self.values = None
            self.name = 'Unknown'

    def parse_arguments(self, extraargs):
        """
        num_observations
        inds
        sample_rate
        freq
        basis
        basis_len
        name
        """

        if 'name' in extraargs:
            self.name = extraargs['name']
        else:
            self.name = 'Convolutional'

        if 'num_observations' in extraargs:
            self.num_observations = extraargs['num_observations']
        else:
            raise ValueError('num_observations not passed to ConvolutionalRegressor')

        if 'impulse_inds' in extraargs:
            self.impulse_inds = extraargs['impulse_inds']
        else:
            raise ValueError('impulse_inds not passed to ConvolutionalRegressor')

        if 'sample_rate' in extraargs:
            self.sample_rate = extraargs['sample_rate']
        else:
            raise ValueError('sample_rate not passed to ConvolutionalRegressor')

        if 'frequency' in extraargs:
            self.frequency = extraargs['frequency']
        else:
            raise ValueError('frequency not passed to ConvolutionalRegressor')

        if 'basis_len' in extraargs:
            self.basis_len = extraargs['basis_len']
        else:
            raise ValueError('basis_len not passed to ConvolutionalRegressor')

        if 'basis' in extraargs:
            self.basis = extraargs['basis']
            if self.basis not in ['sine', 'cosine']:
                raise ValueError('basis must be either \'sine\' or \'cosinea\'')
        else:
            raise ValueError('basis not passed to ConvolutionalRegressor')


register_class(ConvolutionalRegressor)
