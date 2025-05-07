import numpy as np


def tiny(noise=.02):
    from . import design, data, fit, regressors

    # Simple model
    Y = np.random.normal(size=(5000, 1))*noise + .5
    data = data.ContinuousGLMData(Y, 100, 0)

    regressors = [regressors.ConstantRegressor(num_observations=data.num_observations),
                  regressors.TrendRegressor(num_observations=data.num_observations, name='linear')]

    contrasts = [design.Contrast([1, 0], 'Mean'),
                 design.Contrast([0, 1], 'linear')]

    glmdes = design.GLMDesign.initialise(regressors, contrasts)
    model = fit.OLSModel(glmdes, data)

    print('{0:15}: {1} \n{2:15}: {3}'.format('Mean', model.betas[0, 0], 'Linear Trend', model.betas[1, 0]))


def multi_trial(nsamples=2000, ntrials=500, noise=2.5):
    from . import design, data, fit

    # Time-varying model
    Y = np.random.normal(size=(ntrials, nsamples))*noise
    Y = Y + (np.sin(np.linspace(0, np.pi, nsamples)) - .5)

    inds = np.round(nsamples/4).astype(int)
    indt = np.round(ntrials/2).astype(int)

    conditions = np.zeros((ntrials,))
    conditions[:indt] = 1
    conditions[indt:] = 2

    dat = data.TrialGLMData(data=Y, category_list=conditions, sample_rate=100)
    print(dat.info)

    Y[:indt, :inds] += 1
    Y[indt:, :inds] -= .6

    tmp = np.ones((ntrials,))
    tmp[indt:, ] = 1
    tmp[:indt, ] = -1

    regressors = list()
    regressors.append(design.ParametricRegressor(np.linspace(-1, 1, ntrials), 'linear'))
    regressors.append(design.ConditionRegressor(conditions=conditions, trial_codes=1))
    regressors.append(design.ConditionRegressor(conditions=conditions, trial_codes=2))
    regressors.append(design.ParametricRegressor(np.random.random_sample(conditions.shape), 'Reaction Time'))

    contrasts = list()
    contrasts.append(design.Contrast([0, 1, 0, 0], 'Cond 1'))
    contrasts.append(design.Contrast([0, 0, 1, 0], 'Cond 2'))
    contrasts.append(design.Contrast([0, 1, -1, 0], 'Cond 1>2'))
    contrasts.append(design.Contrast([0, 0, 0, 1], 'RT'))

    ftests = list()
    ftests.append(design.FTest([1, 1, 0, 0], 'ME Condition'))
    ftests.append(design.FTest([0, 0, 0, 1], 'ME RT'))

    glmdes = design.GLMDesign.initialise(regressors, contrasts, ftests)
    print(glmdes.ftest_names)

    glmdes.plot_summary()
    model = fit.OLSModel(glmdes, dat)
    import matplotlib.pyplot as plt
    plt.figure()
    plt.subplot(211)
    plt.plot(model.copes.T)
    plt.legend(glmdes.contrast_names)
    plt.title('COPEs')
    plt.subplot(212)
    plt.plot(model.get_tstats().T)
    plt.legend(glmdes.contrast_names)
    plt.title('t-stats')
    plt.show()


def design_from_yaml_trialwise():

    yaml_txt = """
first_level:
  regressors:
    - {name: LinearTrend, regressor: TrendRegressor }
    - {name: PowerTrend,  regressor: TrendRegressor, power: 2 }
    - {name: Famous,      regressor: CategoricalRegressor, codes: 1 2 }
    - {name: Unfamiliar,  regressor: CategoricalRegressor, codes: 3 4 }
    - {name: Scrambled,   regressor: CategoricalRegressor, codes: 5 6 }

  contrasts:
    - {name: Trends, values: 1 1 0 0 0 }
    - {name: Faces, values: 0 0 1 1 0 }
    - {name: Faces>Scrambles, values: 0 0 1 1 -2 }
    - {name: Famous>Unfamiliar, values: 0 0 1 -1 0 }
"""
    import yaml
    from . import util, design
    config = yaml.load(yaml_txt)

    cond_labels = np.tile(np.arange(1, 7), 10)
    dat_info = dict(num_observations=len(cond_labels), condition_list=cond_labels)

    regressors = util.regressors_from_datainfo(config['first_level']['regressors'], dat_info)
    contrasts = util.contrasts_from_dict(config['first_level']['contrasts'])

    des = design.GLMDesign.initialise(regressors, contrasts)
    des.plot_summary()


def design_from_yaml_boxcar():

    yaml_txt = """
first_level:
  regressors:
    - {name: Mean,        regressor: ConstantRegressor }
    - {name: LinearTrend, regressor: TrendRegressor }
    - {name: Power2,      regressor: TrendRegressor, power: 2 }
    - {name: Power4,      regressor: TrendRegressor, power: 4 }
    - {name: Power6,      regressor: TrendRegressor, power: 6 }
    - {name: Famous,      regressor: BoxcarRegressor, trls: [[50,150],[450,600]] }
    - {name: Unfamiliar,  regressor: BoxcarRegressor, trls: [[150,250],[800,1000]] }
    - {name: Scrambled,   regressor: BoxcarRegressor, trls: [[1050,1400]] }

  contrasts:
    - {name: Trends, values: 0 1 1 1 1 0 0 0 }
    - {name: Faces, values: 0 0 0 0 0 1 1 0 }
    - {name: Faces>Scrambles, values: 0 0 0 0 0 1 1 -2 }
    - {name: Famous>Unfamiliar, values: 0 0 0 0 0 1 -1 0 }
"""
    import yaml
    from . import util, design
    config = yaml.load(yaml_txt)

    # Spoof a data_info dict
    dat_info = dict(num_observations=1500)
    regressors = util.regressors_from_datainfo(config['first_level']['regressors'], dat_info)

    contrasts = util.contrasts_from_dict(config['first_level']['contrasts'])

    des = design.GLMDesign.initialise(regressors, contrasts)
    des.plot_summary()


def design_from_yaml_convolutional():

    yaml_txt = """
first_level:
  regressors:
    - {name: Mean,        regressor: ConstantRegressor }
    - {name: LinearTrend, regressor: TrendRegressor }
    - {name: SquareTrend, regressor: TrendRegressor, power: 2 }
    - {name: Cond1_1Hz, regressor: ConvolutionalRegressor, basis: sine,
                    impulse_inds: [[150,700,1200]], frequency: 1, basis_len: 250 }
    - {name: Cond1_2Hz, regressor: ConvolutionalRegressor, basis: sine,
                    impulse_inds: [[150,700,1200]], frequency: 2, basis_len: 250 }
    - {name: Cond1_4Hz,  regressor: ConvolutionalRegressor, basis: sine,
                    impulse_inds: [[150,700,1200]], frequency: 4, basis_len: 250 }
    - {name: Cond2_1Hz, regressor: ConvolutionalRegressor, basis: cosine,
                    impulse_inds: [[300,750,1350]], frequency: 1, basis_len: 250 }
    - {name: Cond2_2Hz, regressor: ConvolutionalRegressor, basis: cosine,
                    impulse_inds: [[300,750,1350]], frequency: 2, basis_len: 250 }
    - {name: Cond4_4Hz, regressor: ConvolutionalRegressor, basis: cosine,
                    impulse_inds: [[300,750,1350]], frequency: 4, basis_len: 250 }

  contrasts:
    - {name: Trends,          values: 1 1 1 0 0 0 0 0 0 }
    - {name: Condition1,      values: 0 0 0 1 1 1 0 0 0 }
    - {name: Condition2,      values: 0 0 0 0 0 0 1 1 1}
"""
    import yaml
    from . import util, design
    config = yaml.load(yaml_txt)

    # Spoof a data_info dict
    dat_info = dict(num_observations=1500, sample_rate=250)
    regressors = util.regressors_from_datainfo(config['first_level']['regressors'], dat_info)

    contrasts = util.contrasts_from_dict(config['first_level']['contrasts'])

    des = design.GLMDesign.initialise(regressors, contrasts)
    des.plot_summary()


def design_from_yaml_group():

    yaml_txt = """
group_level:

  tag_regressors:
    - {tag: subject, mode: dummy_code}
    - {tag: session, mode: parametric}
    - {tag: reaction_time, mode: parametric}

datasets:
  - { name: sub01_sess01,
      file: /path/to/data/sub001/run_01_sss-epo.fif,
      subject: 1, session: 1, reaction_time: 110 }
  - { name: sub01_sess02,
      file: /path/to/data/sub001/run_02_sss-epo.fif,
      subject: 1, session: 2, reaction_time: 120 }
  - { name: sub01_sess03,
      file: /path/to/data/sub001/run_03_sss-epo.fif,
      subject: 1, session: 3, reaction_time: 110 }
  - { name: sub01_sess05,
      file: /path/to/data/sub001/run_01_sss-epo.fif,
      subject: 2, session: 1, reaction_time: 150 }
  - { name: sub01_sess04,
      file: /path/to/data/sub001/run_02_sss-epo.fif,
      subject: 2, session: 2, reaction_time: 160 }
  - { name: sub01_sess06,
      file: /path/to/data/sub001/run_03_sss-epo.fif,
      subject: 2, session: 3, reaction_time: 120 }
  - { name: sub02_sess01,
      file: /path/to/data/sub001/run_01_sss-epo.fif,
      subject: 3, session: 1, reaction_time: 180 }
  - { name: sub02_sess02,
      file: /path/to/data/sub001/run_02_sss-epo.fif,
      subject: 3, session: 2, reaction_time: 150 }
  - { name: sub02_sess03,
      file: /path/to/data/sub001/run_03_sss-epo.fif,
      subject: 3, session: 3, reaction_time: 120 }
"""

    import yaml
    from . import util, design
    config = yaml.load(yaml_txt)

    regressors, contrasts = util.group_regressors_from_dict(config['group_level'], config['datasets'])

    des = design.GLMDesign.initialise(regressors, contrasts)
    des.plot_summary(summary_lines=False)


def group():

    yaml_txt = """
first_level:
  regressors:
    - {name: LinearTrend, regressor: TrendRegressor }
    - {name: PowerTrend,  regressor: TrendRegressor, power: 2 }
    - {name: Words,       regressor: CategoricalRegressor, codes: 1 2 }
    - {name: Nonwords,    regressor: CategoricalRegressor, codes: 3 4 }

  contrasts:
    - {name: Trends, values: 1 1 0 0 }
    - {name: Words, values: 0 0 1 0 }
    - {name: Nonwords, values: 0 0 0 1 }
    - {name: Words>Nonwords, values: 0 0 1 -1 }

group_level:
  tag_regressors:
    - {tag: subject, mode: dummy_code}
    - {tag: session, mode: dummy_code}
    - {tag: diagnosis, mode: contrast}
    - {tag: reaction_time, mode: parametric}

datasets:
  - { runname: sub01_sess01,
      subject: 1, session: 1, reaction_time: 110, diagnosis: 0 }
  - { runname: sub01_sess02,
      subject: 1, session: 2, reaction_time: 120, diagnosis: 0 }
  - { runname: sub01_sess03,
      subject: 1, session: 3, reaction_time: 110, diagnosis: 0 }
  - { runname: sub02_sess01,
      subject: 2, session: 1, reaction_time: 150, diagnosis: 0 }
  - { runname: sub02_sess02,
      subject: 2, session: 2, reaction_time: 160, diagnosis: 0 }
  - { runname: sub02_sess03,
      subject: 2, session: 3, reaction_time: 120, diagnosis: 0 }
  - { runname: sub02_sess01,
      subject: 3, session: 1, reaction_time: 180, diagnosis: 0 }
  - { runname: sub03_sess02,
      subject: 3, session: 2, reaction_time: 150, diagnosis: 0 }
  - { runname: sub03_sess03,
      subject: 3, session: 3, reaction_time: 120, diagnosis: 0 }
  - { runname: sub04_sess03,
      subject: 4, session: 1, reaction_time: 90, diagnosis: 1 }
  - { runname: sub04_sess01,
      subject: 4, session: 2, reaction_time: 120 , diagnosis: 1 }
  - { runname: sub04_sess02,
      subject: 4, session: 3, reaction_time: 100, diagnosis: 1 }
  - { runname: sub05_sess01,
      subject: 5, session: 1, reaction_time: 170, diagnosis: 1 }
  - { runname: sub05_sess02,
      subject: 5, session: 2, reaction_time: 160, diagnosis: 1 }
  - { runname: sub05_sess03,
      subject: 5, session: 3, reaction_time: 150, diagnosis: 1 }
  - { runname: sub06_sess03,
      subject: 6, session: 1, reaction_time: 200, diagnosis: 1 }
  - { runname: sub06_sess02,
      subject: 6, session: 2, reaction_time: 190, diagnosis: 1 }
  - { runname: sub06_sess03,
      subject: 6, session: 3, reaction_time: 190, diagnosis: 1 }
"""
    from . import design, data, fit, util

    import yaml
    config = yaml.load(yaml_txt)

    # First Level
    models = list()
    first_level_contrasts = util.contrasts_from_dict(config['first_level']['contrasts'])
    for ii in range(len(config['datasets'])):

        dat = data.TrialGLMData(np.random.randn(120, 100), category_list=np.random.choice(np.arange(1, 5), 120))
        reg = util.regressors_from_datainfo(config['first_level']['regressors'], dat.info)

        des = design.GLMDesign.initialise(reg, first_level_contrasts)
        models.append(fit.OLSModel(des, dat))

    # Group Level
    group_data = data.GroupData(models, config)
    group_reg = group_data.get_simple_regressors(dummy_code=['subject'],
                                                 contrast=['diagnosis'],
                                                 parametric=['reaction_time'])

    group_contrasts = list()
    group_contrasts.append(design.Contrast([0, 0, 0, 0, 0, 0, 1, 0], name='Diagnosis'))
    group_contrasts.append(design.Contrast([0, 0, 0, 0, 0, 0, 0, 1], name='ReactionTime'))

    group_des = design.GLMDesign.initialise(group_reg, group_contrasts)
    group_des.plot_summary()


def example_permutations():

    from . import design, data, fit, permutations

    # Simulated data with two patches
    X = np.random.randn(20, 24, 24)
    # First patch has non-zero mean
    X[:, 3:8, 3:8] += 2
    # Second patch correlates with something
    covariate = np.random.randn(20)*3
    X[:, 6:10, 6:10] += covariate[:, None, None]

    data = data.TrialGLMData(data=X, covariate=covariate, dim_labels=['Trials', 'Time', 'Frequency'])

    # Simple design to capture mean and correlation
    DC = design.DesignConfig()
    DC.add_regressor(name='mean', rtype='Constant')
    DC.add_regressor(name='covariate', rtype='Parametric', datainfo='covariate')
    DC.add_simple_contrasts()

    design = DC.design_from_datainfo(data.info)
    model = fit.OLSModel(design, data)

    import matplotlib.pyplot as plt
    plt.figure()
    for cont in range(2):

        # Simplest permutations - treat each cell as an independent test with its
        # own null distribution
        P = permutations.Permutation(design, data, cont, 500, metric='tstats')
        sig_simple = P.get_sig_at_percentile(99)  # Thresh is a 12x12 matrix
        #sig_simple = model.tstats[cont, ...] > thresh

        # Max-stat permutations - correct for multiple comparisons by pooling null across tests.
        MSP = permutations.MaxStatPermutation(design, data, cont, 500, metric='tstats', pooled_dims=(1, 2))
        thresh = MSP.get_thresh(99)  # This is a single number as we pool overeverything
        sig_maxstat = model.tstats[cont, ...] > thresh

        # Max-stat permutations - correct for multiple comparisons by pooling null across tests.
        tstat_args = {'varcope_smoothing': 5, 'smooth_dims': (1, 2)}
        MSP = permutations.MaxStatPermutation(design, data, cont, 500,
                                              metric='tstats',
                                              pooled_dims=(1, 2),
                                              tstat_args=tstat_args)
        thresh = MSP.get_thresh(99)  # This is a single number as we pool overeverything
        sig_maxstat = model.tstats[cont, ...] > thresh

        # Cluster permutations - detect contiguous regions containing effects.
        CP = permutations.ClusterPermutation(design, data, cont, 500,
                                             metric='tstats',
                                             tail=-1,
                                             cluster_forming_threshold=2.3,
                                             pooled_dims=[1, 2])
        cluster_masks, cluster_stats = CP.get_sig_clusters(data, 99)

        plt.subplot(2, 4, 1+4*cont)
        plt.pcolormesh(model.tstats[cont, ...])
        plt.title('Observed data')
        plt.subplot(2, 4, 2+4*cont)
        plt.pcolormesh(sig_simple)
        plt.title('Simple Permutations')
        plt.subplot(2, 4, 3+4*cont)
        plt.pcolormesh(sig_maxstat)
        plt.title('MaxStat Permutations')
        plt.subplot(2, 4, 4+4*cont)
        plt.pcolormesh(cluster_masks)
        plt.title('Cluster Permutations')
    plt.show()


def check_outliers(nsamples=2000, ntrials=50, noise=2.5):
    from . import design, data

    Y = np.random.normal(size=(ntrials, nsamples))*noise
    cov = np.random.normal(size=(ntrials,))

    # Add regressor outliers
    cov[25] = 5
    cov[125] = 6.7

    indt = np.round(ntrials/2).astype(int)

    conditions = np.zeros((ntrials,))
    conditions[:indt] = 1
    conditions[indt:] = 2

    Y[:indt, :] += 1
    Y[indt:, :] -= .6
    Y = Y * cov[:, None]

    # Add data outliers
    Y[30, :] += 10
    Y[:, 100] -= 10

    tmp = np.ones((ntrials,))
    tmp[indt:, ] = 1
    tmp[:indt, ] = -1

    dat = data.TrialGLMData(data=Y, category_list=conditions, sample_rate=100, cov=cov)
    print(dat.info)

    DC = design.DesignConfig()
    DC.add_regressor('Categorical', name='Cond1', codes=1)
    DC.add_regressor('Categorical', name='Cond2', codes=2)
    DC.add_regressor('Parametric', name='Cov', datainfo='cov', preproc='z')
    DC.add_simple_contrasts()

    des = DC.design_from_datainfo(dat.info)
    print(des)
