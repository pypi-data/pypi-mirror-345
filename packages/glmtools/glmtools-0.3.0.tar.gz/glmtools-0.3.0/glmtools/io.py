import os
import numpy as np
from . import data


def load_glm(X):

    from anamnesis import obj_from_hdf5file
    return obj_from_hdf5file(X, 'data')


def load_data(filepath, datatype, dataformat):

    if dataformat == 'mne':
        if datatype == 'trial':
            return load_mne_epochs(filepath)
        elif datatype == 'continuous':
            return load_mne_raw(filepath)

    elif dataformat == 'npy':
        if datatype == 'trial':
            return load_npy_trial(filepath)

    elif dataformat == 'glm':
        return load_glm(filepath)

    else:
        raise ValueError('dataformat: {0} or datatype: {1} not recognised'.format(dataformat, datatype))


def load_npy_trial(filepath):

    dat = np.load(filepath)
    infopath = filepath[:-4] + '_info.pkl'

    import pickle
    info = pickle.load(open(infopath, 'rb'))

    d = data.TrialGLMData(data=dat, category_list=info['category_list'])

    for k in info.keys():
        print(k)
        d.info[k] = info[k]

    return d


def load_mne_raw(filepath):

    import mne
    raw = mne.read_raw(filepath)

    d = data.ContinuousGLMData(data=raw.get_data(),
                               sample_rate=raw.info['fsample'],
                               start_time=0)

    return d


def load_mne_epochs(X):

    import mne
    if isinstance(X, str) and os.path.isfile(X):
        epochs = mne.read_epochs(X)
    elif isinstance(X, (mne.epochs.EpochsFIF, mne.Epochs)):
        epochs = X

    d = data.TrialGLMData(data=epochs.get_data(),
                          category_list=epochs.events[:, 2],
                          sample_rate=epochs.info['sfreq'],
                          time_dim=2,
                          dim_labels=list(('Trials', 'Channels', 'Times')))

    return d
