#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import numpy as np
from . import design, io, data
import yaml
import os
from anamnesis import AbstractAnam, register_class, obj_from_hdf5file
from scipy.stats import zscore


class Study:

    hdf5_outputs = ['_config', 'studyname', 'studydir', 'first_level', 'group_level', 'datasets',
                    'datatype', 'dataformat', 'first_level_contrasts',
                    'first_level_ftests', 'group_level_contrasts', 'group_level_ftests']

    def __init__(self, yaml_file=None):
        AbstractAnam.__init__(self)

        if yaml_file is None:
            return

        self._config = yaml.load(open(yaml_file, 'r'))

        self.studyname = self._config['studyname']
        self.studydir = self._config['studydir']

        self.first_level = self._config['first_level']
        self.group_level = self._config['group_level']

        self.datasets = self._config['datasets']
        self.datatype = self._config['datatype']
        self.dataformat = self._config['dataformat']

        self.first_level_contrasts = None
        self.first_level_ftests = None
        self.group_level_contrasts = None
        self.group_level_ftests = None

    def initialise_study(self):

        # Make results directory if needed
        if not os.path.exists(self.studydir):
            os.makedirs(self.studydir)

        # Check we can write to it
        if os.access(self.studydir, os.W_OK) is False:
            Warning('Write access to study dir denied! \n{0}'.format(self.studydir))

        # Get first and group level contrasts and ftests, regressors are generated per dataset
        if 'contrasts' in self.first_level:
            self.first_level_contrasts = contrasts_from_dict(self.first_level['contrasts'])
        if 'ftests' in self.first_level:
            self.first_level_ftests = ftests_from_dict(self.first_level['ftests'])

        if 'contrasts' in self.group_level:
            self.group_level_contrasts = contrasts_from_dict(self.group_level['contrasts'])
        if 'ftests' in self.group_level:
            self.group_level_ftests = ftests_from_dict(self.group_level['ftests'])

        self.outbase = '{0}/{1}'.format(self.studydir, self.studyname)

    def get_first_level_info(self, run):

        if isinstance(run, int):
            if run >= self.num_datasets:
                raise ValueError('Requested run {0} but there are only {1} runs'.format(run, self.num_datasets))
            else:
                return self.datasets[run]

        elif isinstance(run, str):
            for dd in self.datasets:
                if dd['runname'] == run:
                    return dd
            raise ValueError('Runname {0} not found in config'.format(run))

        else:
            raise ValueError('Runname {0} not recognised, please use either the dataset name or number'.format(run))

    def get_first_level(self, run):

        dat = self.get_first_level_info(run)
        session_data = io.load_data(dat['file'], self.datatype, self.dataformat)
        session_reg = regressors_from_datainfo(self.first_level['regressors'],
                                               session_data.info)
        session_design = design.GLMDesign.initialise(session_reg,
                                                     self.first_level_contrasts,
                                                     self.first_level_ftests)
        outname = '{0}_{1}'.format(self.outbase, dat['runname'])

        return (session_design, session_data, outname)

    def first_level_generator(self):

        for dat in self.datasets:
            session_data = io.load_data(dat['file'], self.datatype, self.dataformat)
            session_reg = regressors_from_datainfo(self.first_level['regressors'],
                                                   session_data.info)
            session_design = design.GLMDesign.initialise(session_reg,
                                                         self.first_level_contrasts,
                                                         self.first_level_ftests)
            outname = '{0}_{1}'.format(self.outbase, dat['runname'])

            yield (session_design, session_data, outname)

    def get_group_level(self):

        first_levels = list()
        for dat in self.datasets:

            outname = '{0}_{1}.hdf5'.format(self.outbase, dat['runname'])
            first_levels.append(obj_from_hdf5file(outname, 'model'))

        group_data = data.HigherLevelData(models=first_levels,
                                          group_conf=self.group_level, datasets=self.datasets)

        if 'tag_regressors' in self.group_level:
            group_design = tag_design_from_datainfo(self.group_level['tag_regressors'],
                                                    group_data.info)
        else:
            group_reg = regressors_from_datainfo(self.group_level['regressors'],
                                                 group_data.info)
            group_design = design.GLMDesign.initialise(group_reg,
                                                       self.group_level_contrasts,
                                                       self.group_level_ftests)

        return (group_design, group_data)

    @property
    def num_datasets(self):

        return len(self.datasets)


register_class(Study)


#############

def standardise_data(X):
    """
    zscore dataset across observations [nobservations x nsignals]
    """

    return (X - X.mean(axis=0)) / X.std(axis=0)

# Design helpers


def ftests_from_dict(config, regs=None):

    ftests = list()
    for con in config:
        if isinstance(con['values'], str):
            vals = np.array(con['values'].split()).astype(float)
        elif isinstance(con['values'], int):
            vals = [con['values']]
        elif isinstance(con['values'], list):
            vals = con['values']
        elif isinstance(con['values'], tuple):
            vals = list(con['values'])
        elif isinstance(con['values'], dict):
            if regs is None:
                return ValueError('Missing contrast info, cannot define f-test')
            vals = np.zeros(len(regs),)
            rnames = [r.name for r in regs]
            for key in con['values'].keys():
                vals[rnames.index(key)] = con['values'][key]
        ftests.append(design.FTest(name=con['name'], values=vals))

    # Sanity check
    if len(set([len(a.values) for a in ftests])) > 1:
        raise ValueError('FTest lengths are mismatched')

    return ftests


def contrasts_from_dict(config, regs=None):

    contrasts = list()
    for con in config:
        if isinstance(con['values'], str):
            vals = np.array(con['values'].split()).astype(float)
        elif isinstance(con['values'], int):
            vals = [con['values']]
        elif isinstance(con['values'], list):
            vals = con['values']
        elif isinstance(con['values'], tuple):
            vals = list(con['values'])
        elif isinstance(con['values'], dict):
            if regs is None:
                return ValueError('Missing regressor info, cannot define contrast')
            vals = np.zeros(len(regs),)
            rnames = [r.name for r in regs]
            for key in con['values'].keys():
                vals[rnames.index(key)] = con['values'][key]
        contrasts.append(design.Contrast(name=con['name'], values=vals))

    # Sanity check
    if len(set([len(a.values) for a in contrasts])) > 1:
        raise ValueError('Contrast lengths are mismatched')

    return contrasts


def group_regressors_from_dict(group_level, datasets, nobservations=None,
                               condition_labels=None):

    # This whole function needs replacing - group level approach has changed a lot

    #if 'regressors' in group_level.keys():
    #    regressors = regressors_from_dict(group_level['regressors'],
    #                                      nobservations=nobservations,
    #                                      condition_labels=condition_labels,
    #                                      datasets=datasets)
    #else:
    #    regressors = list()
    regressors = list()

    if 'contrasts' in group_level.keys():
        contrasts = contrasts_from_dict(group_level['contrasts'])
    else:
        contrasts = list()

    if 'tag_regressors' in group_level.keys():
        dummies = group_level['tag_regressors']

        for idum in dummies:

            tag = idum['tag']
            if 'contrast_type' in idum.keys():
                contrast_type = idum['contrast_type']
            else:
                contrast_type = None
            regressors, contrasts = add_tag_regressor(regressors, contrasts,
                                                      tag, datasets, mode=idum['mode'],
                                                      contrast_type=contrast_type)

    return regressors, contrasts


def add_tag_regressor(regressors, contrasts, tag, datasets=None, tag_vect=None,
                      basename=None, mode='dummy_code', contrast_type=None):

    if basename is None:
        basename = str(tag)

    if tag_vect is None:
        tag_vect = [x[tag] for x in datasets]

    if mode == 'dummy_code':
        # Add each value of tag as main effect

        tags = np.unique(tag_vect)
        num_old_regressors = len(regressors)
        num_new_regressors = len(tags)

        for tt in tags:

            regressors.append(design.ConditionRegressor(conditions=tag_vect, trial_codes=tt,
                                                        name=basename+str(tt)))

        for c in contrasts:
            c.values = np.r_[c.values, np.zeros((num_new_regressors,))]

        if contrast_type == 'merge':
            new_contrast = np.r_[np.zeros((num_old_regressors,)), np.ones((num_new_regressors,))]
            contrasts.append(design.Contrast(new_contrast, name=basename))
        elif contrast_type == 'split':
            for ii in range(num_new_regressors):
                new_contrast = np.zeros((num_old_regressors+num_new_regressors,))
                new_contrast[num_old_regressors+ii] = 1
                contrasts.append(design.Contrast(new_contrast, name=basename+str(tt)))

    elif mode == 'parametric':
        # Add tag as parametric variable

        num_old_regressors = len(regressors)

        regressors.append(design.ParametricRegressor(values=tag_vect, name=basename, preproc='z'))

        for c in contrasts:
            c.values = np.r_[c.values, np.zeros((1,))]

        new_contrast = np.r_[np.zeros((num_old_regressors,)), np.array((1,))]
        contrasts.append(design.Contrast(new_contrast, name=basename))

    return regressors, contrasts


def tag_design_from_datainfo(tag_reg, data_info):

    regs = []
    conts = []

    from . import regressors
    for tr in tag_reg:

        if tr['mode'] == 'dummy_code':
            tags = np.unique(data_info[tr['tag']])
            num_old_regressors = len(regs)
            num_new_regressors = len(tags)

            r = regressors.CategoricalRegressor

            for t in tags:
                regs.append(r(category_list=data_info[tr['tag']],
                            codes=t,
                            name=tr['tag']+str(t)))

            new_contrast = np.r_[np.zeros((num_old_regressors,)), np.ones((num_new_regressors,))]
            conts.append(design.Contrast(new_contrast, name=tr['tag']))
            if len(conts) > 1:
                for c in conts[:-1]:
                    c.values = np.r_[c.values, np.zeros((num_new_regressors,))]

        elif tr['mode'] == 'group_mean':
            num_old_regressors = len(regs)

            tags = tuple(tr['tag'].split(' '))

            tag_vect = [np.atleast_2d(data_info[t]) for t in tags]
            tag_vect = np.concatenate(tag_vect, axis=0)

            groups = np.unique(tag_vect, axis=1)
            group_inds = [np.where((tag_vect.T == groups[:, t]).all(axis=1))[0] for t in range(groups.shape[1])]

            num_new_regressors = groups.shape[1]
            if len(conts) > 1:
                for c in conts[:-1]:
                    c.values = np.r_[c.values, np.zeros((num_new_regressors,))]

            # Add grand mean contrast
            conts.append(design.Contrast(np.r_[np.zeros((num_old_regressors,)),
                                               np.ones((num_new_regressors,))],
                                         name='_'.join(tags)))

            r = regressors.CategoricalRegressor
            for t in range(groups.shape[1]):

                name = [tags[ii] + str(groups[ii, t]) for ii in range(len(tags))]
                name = '_'.join(name)

                regs.append(r(category_list=np.arange(tag_vect.shape[1]),
                              codes=group_inds[t],
                              name=name))

                new_contrast = np.zeros((num_old_regressors+num_new_regressors,))
                new_contrast[num_old_regressors+t] = 1

                conts.append(design.Contrast(new_contrast, name=name))

            for t in range(groups.shape[0]):

                new = (groups[t, :] - groups[t, :].mean()) / groups[t, :].std()
                conts.append(design.Contrast(np.r_[np.zeros((num_old_regressors,)), new],
                                             name=tags[t]))

        elif tr['mode'] == 'parametric':
            # Add tag as parametric variable

            if 'mask' not in tr.keys():
                mask = np.ones((1, data_info['num_observations'])).astype(bool)
            else:
                groups = np.unique(data_info[tr['mask']])
                mask = np.array([(data_info[tr['mask']] == t) for t in groups])

            for ii in range(mask.shape[0]):
                num_old_regressors = len(regs)

                vals = np.array(data_info[tr['tag']])

                name = tr['tag']
                if 'mask' in tr.keys():
                    mask_inds = np.where(mask[ii, :])[0]
                    vals[~mask[ii, :]] = 0
                    vals = vals.astype(float)
                    name += '_' + tr['mask'] + str(groups[ii])
                    # do preproc here rather than in regressor
                    vals[mask_inds] = zscore(vals[mask_inds])
                    preproc = None
                else:
                    preproc = 'z'

                regs.append(regressors.ParametricRegressor(values=vals,
                                                           name=name,
                                                           preproc=preproc,
                                                           **data_info))

                new_contrast = np.r_[np.zeros((num_old_regressors,)), np.array((1,))]

                conts.append(design.Contrast(new_contrast, name=name))

                if len(conts) > 1:
                    for c in conts[:-1]:
                        c.values = np.r_[c.values, 0]

    return design.GLMDesign.initialise(regs, conts)


def regressors_from_datainfo(reg_conf, data_info):

    from . import regressors

    # Load first level regressors
    data_regressors = list()
    for reg in reg_conf:

        reg = reg.copy()

        reg_type = reg.pop('regressor')
        if reg_type == 'MeanEffectsRegressor':
            groups = data_info.get(reg['datainfo'])
            basename = reg['name'] + '{0}'
            for g in np.unique(groups):
                reg = regressors.CategoricalRegressor(name=basename.format(g),
                                                      codes=g,
                                                      category_list=groups)
                data_regressors.append(reg)

        elif reg_type == 'Interaction':
            print(reg)
            reg = regressors.InteractionRegressor()

        else:
            r = getattr(regressors, reg_type)

            if r is None:
                raise ValueError('Regressor type {0} not recognised'.format(reg_type))

            # Remove data_info keys if they already exist in regressor config
            # - regressor config takes precedence
            for key in reg:
                data_info.pop(key, None)

            arg_dict = {**reg, **data_info}

            data_regressors.append(r(**arg_dict))

    return data_regressors


def groupinfo_from_dict(config):

    info = dict(num_inputs=len(config['datasets']),
                group_conf=config)

    kys = config['datasets'][0].keys()
    for ky in config['datasets'][0].keys():
        info[ky] = [d[ky] for d in config['datasets']]
    info['dataset_keys'] = kys

    return info


def compute_t_stats(copes, varcopes, temporal_varcope_smoothing=None, smoothing_window=np.hanning, time_dim=None):

    if temporal_varcope_smoothing == 'avg':

        dim_len = varcopes.shape[time_dim]
        varcopes = varcopes.mean(time_dim)
        varcopes = np.expand_dims(varcopes, time_dim)

        denom = np.repeat(np.sqrt(varcopes), dim_len, axis=time_dim)

    elif temporal_varcope_smoothing is not None:
        # Create window normalised to have area of 1
        w = smoothing_window(temporal_varcope_smoothing)
        w = w / w.sum()

        func = lambda m: np.convolve(m, w, mode='same')  # noqa E731 - skip lambda style warning
        varcopes = np.apply_along_axis(func, time_dim, arr=varcopes)

        denom = np.sqrt(varcopes)

    else:
        denom = np.sqrt(varcopes)

    # Compute t-values
    return copes / denom
