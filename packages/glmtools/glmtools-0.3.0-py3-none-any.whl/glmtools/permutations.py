#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import numpy as np
from . import fit
import sys
from copy import deepcopy

from scipy import ndimage, stats


class Permutation:
    """
    Passed in a design and a contrast.
    1. id perm type
    2. set output size
    3. start iteration
      a. shuffle model with apply_permutation
      b. fit new model
      c. extract stat with _extrat_perm_stat
    4. store null dist
    """

    def __init__(self, design, data, contrast_idx, nperms,
                 metric='copes', nprocesses=1, tail=0, perm_type='auto',
                 tstat_args=None, fit_class=fit.OLSModel, verbose=False):
        from copy import deepcopy
        self._design = deepcopy(design)
        self.nperms = nperms
        self.tail = tail
        self.tstat_args = {} if tstat_args is None else tstat_args
        self.contrast_idx = contrast_idx
        self.cinds = np.where(self._design.contrasts[contrast_idx, :] != 0.)[0]
        self.cname = self._design.contrast_names[contrast_idx]
        self.nprocesses = nprocesses
        self.fit_class = fit_class
        self.verbose = verbose

        if metric not in ['tstats', 'copes']:
            msg = "Permutation metric must be either 'tstats' or 'copes'"
            msg += "- ('{0}' was passed in)".format(metric)
            raise ValueError(msg)
        self.perm_metric = metric

        self.rtype = self._get_rtype(contrast_idx)
        self.ctype = self._design.contrast_list[contrast_idx].ctype

        if perm_type == 'auto':
            self.perm_type = self._get_perm_type(self.rtype, self.ctype)
        else:
            self.perm_type = perm_type
        self.data_dims = data.data.shape
        self.data_dim_labels = data.info['dim_labels']

        self._print_info()
        self.permute(data)

    def _print_info(self):
        _print_info(self)

    def _get_rtype(self, idx):
        rtype = [self._design.regressor_list[ii].rtype for ii in self.cinds]
        rtype = np.unique(rtype)
        if len(rtype) > 1:
            raise ValueError('Contrast is mixing multiple regressor types')
        else:
            rtype = rtype[0]
        return rtype

    def _get_null_dims(self, dims):
        # everything is an array for sanity

        # Create shape of null
        dims = np.atleast_1d(dims[1:])

        return (self.nperms, *dims)

    def _extract_perm_stat(self, null):
        'get stat out somehow'
        return null

    def _compute_model_stat(self, des, data):

        f = self.fit_class(des, data)
        if self.perm_metric == 'tstats':
            # Use defaults
            ret = f.get_tstats(**self.tstat_args)
        else:
            ret = getattr(f, self.perm_metric)

        return ret[self.contrast_idx, ...]

    def _get_perm_type(self, rtype, ctype):
        'sign-flip etc'
        mode = None
        if rtype == 'Constant':
            mode = 'sign-flip'
        elif rtype == 'Categorical':
            if ctype == 'Differential':
                mode = 'row-shuffle'
            else:
                mode = 'sign-flip'
        elif rtype == 'Parametric':
            mode = 'row-shuffle'

        if mode is None:
            raise ValueError('unable to determine mode')
        else:
            return mode

    def _run_perm(self, data, first):
        """
        data
        first = False
        fit = fit.OLSModel
        tstat_args = {}
        perm_stat_args={}
        """

        np.random.seed()

        if first:
            # Don't permute design matrix
            perm = self._compute_model_stat(self._design, data)
        else:
            perm_design = self.permute_design_matrix()
            perm = self._compute_model_stat(perm_design, data)

        perm_stat = self._extract_perm_stat(perm)
        return perm_stat

    def permute_design_matrix(self):

        return permute_design_matrix(self._design, self.cinds, self.perm_type)

    def permute(self, data):

        null_dims = self._get_null_dims(data.data.shape)
        nulls = np.zeros(null_dims)
        nulls[0, ...] = self._run_perm(data, first=True)

        #for ii in range(1, self.nperms):
        #    nulls[ii, ...] = self._run_perm(data, first=False, fit=fit,
        #                                    tstat_args=tstat_args,
        #                                    perm_stat_args=kwargs)

        import multiprocessing as mp
        #p = mp.Pool(processes=self.nprocesses)
        args = [(data, False) for ii in range(1, self.nperms)]

        with mp.Pool(processes=self.nprocesses) as p:
            res = p.starmap(self._run_perm, args)

        nulls[1:, ...] = np.array(res)

        self.nulls = nulls

    def get_thresh(self, percentiles):

        if self.nulls is None:
            print('Fit permutations first!')
        else:
            return np.nanpercentile(self.nulls, percentiles, axis=0)

    def get_sig_at_percentile(self, percentile, tail=0):

        thresh = self.get_thresh(percentile)

        if tail == 1:
            return self.nulls[0, ...] > thresh
        elif tail == -1:
            return self.nulls[0, ...] < thresh
        elif tail == 0:
            return np.abs(self.nulls[0, ...]) > thresh


def _print_info(P):
    msg = "Permuting contrast {0} with mode={1}"
    print(msg.format(P._design.contrast_list[P.contrast_idx], P.perm_type))
    print("\tComputing {0} permutations".format(P.nperms))
    if P.tstat_args.get('varcope_smoothing') is not None:
        labels = [P.data_dim_labels[x] for x in np.atleast_1d(P.tstat_args.get('smooth_dims'))]
        msg = "\tApplying varcope smoothing of {0} to dims {1}"
        print(msg.format(P.tstat_args.get('varcope_smoothing'), labels))


def permute_design_matrix(design, cinds, perm_type):

    X = design.design_matrix.copy()
    if perm_type == 'sign-flip':
        #perm_inds = np.random.permutation(np.tile([1, -1], int(X.shape[0]/2)))
        #if np.remainder(X.shape[0], 2) == 1:
        #    perm_inds = np.r_[perm_inds, np.random.choice([1, -1])]
        perm_inds = np.random.choice([1, -1], X.shape[0])
        X[:, cinds] = X[:, cinds] * perm_inds[:, None]
    elif perm_type == 'row-shuffle':
        perm_inds = np.random.permutation(X.shape[0])
        ix = np.ix_(perm_inds, cinds)  # np.ix allows us to apply indexing to both dims
        X[:, cinds] = X[ix]
    elif perm_type == 'roll':
        roll_len = np.random.randint(0, X.shape[0])
        for idx in cinds:
            X[:, idx] = np.roll(X[:, idx], roll_len)

    perm_design = deepcopy(design)
    perm_design.design_matrix = X

    return perm_design


class MaxStatPermutation(Permutation):

    def __init__(self, *args, **kwargs):
        self.pooled_dims = kwargs.pop('pooled_dims', [])
        super().__init__(*args, **kwargs)

    def _get_null_dims(self, dims):
        # everything is an array for sanity
        self.pooled_dims = self.pooled_dims

        dims = np.atleast_1d(dims)
        dim_range = np.array(np.arange(len(dims)))

        # First dim is always changed by GLM
        self.nonpooled_dims = np.setdiff1d(dim_range[1:], self.pooled_dims)

        # Create shape of null
        null_dims = (self.nperms, *dims[self.nonpooled_dims])

        labels = [self.data_dim_labels[x] for x in np.atleast_1d(self.pooled_dims)]
        print('\tTaking max-stat across {0} dimensions'.format(labels))

        return null_dims

    def _extract_perm_stat(self, null):

        # Adjust as contrasts dim has been removed
        pd = np.array(self.pooled_dims) - 1
        if isinstance(pd, int) or np.atleast_1d(pd).shape[0] == 1:
            tmp = np.nanmax(np.abs(null), axis=pd)
        elif isinstance(pd, np.ndarray):
            tmp = np.nanmax(np.abs(null), axis=tuple(pd))

        return tmp


class ClusterPermutation(Permutation):

    def __init__(self, *args, **kwargs):
        self.pooled_dims = kwargs.pop('pooled_dims', [])
        self.stat_power = kwargs.pop('stat_power', 1)
        self.cluster_forming_threshold = kwargs.pop('cluster_forming_threshold', [])
        super().__init__(*args, **kwargs)

    def _print_info(self):
        super()._print_info()

        labels = [self.data_dim_labels[x] for x in np.atleast_1d(self.pooled_dims)]
        print('\tFinding clusters in {0} dimensions'.format(labels))

    def _get_null_dims(self, dims):
        # everything is an array for sanity
        dims = np.atleast_1d(dims)
        dim_range = np.array(np.arange(len(dims)))

        # First dim is always changed by GLM
        self.nonpooled_dims = np.setdiff1d(dim_range[1:], self.pooled_dims)

        # Create shape of null
        null_dims = (self.nperms, *dims[self.nonpooled_dims])

        return null_dims

    def _extract_clusters(self, null):
        """
        Return the cluster masks and values of clusters in a dataset
        """

        nonpooled_dims = np.array(self.nonpooled_dims) - 1  # adjust as contrasts dim has been removed
        cluster_masks, cluster_stats = _find_clusters(null,
                                                      self.cluster_forming_threshold,
                                                      nonpooled_dims,
                                                      stat_power=self.stat_power,
                                                      tail=self.tail)

        return cluster_masks, cluster_stats

    def _extract_perm_stat(self, null, ret_clusters=False):
        """
        Return value of largest cluster in each of the nonpooled dimensions

        """
        cluster_masks, cluster_stats = self._extract_clusters(null)
        pooled_dims = np.array(self.pooled_dims) - 1

        cluster_values = np.zeros_like(null)
        for c in range(len(cluster_stats)):
            cluster_values[cluster_masks == c + 1] = cluster_stats[c]

        # Largest cluster value for each of the nonpooled dimensions
        if self.tail == 1:
            cluster_max_per_dim = np.max(cluster_values, axis=tuple(pooled_dims))
        elif self.tail == -1:
            # Take the abs of lower end here - not sure if that is right...
            cluster_max_per_dim = np.abs(np.min(cluster_values, axis=tuple(pooled_dims)))
        elif self.tail == 0:
            cluster_max_per_dim = np.max(np.abs(cluster_values), axis=tuple(pooled_dims))

        return cluster_max_per_dim

    def _extract_perm_stat_old(self, null, ret_clusters=False, **kwargs):

        cluster_forming_threshold = self.perm_args.get('cluster_forming_threshold')
        stat_power = self.perm_args.get('stat_power', 1)

        nonpooled_dims = np.array(self.nonpooled_dims) - 1  # adjust as contrasts dim has been removed
        cluster_slices, cluster_stats = _find_clusters(null, cluster_forming_threshold,
                                                       nonpooled_dims,
                                                       stat_power)

        if len(nonpooled_dims) == 0:
            cluster_stats_nonpooled = np.max(cluster_stats)
            cluster_ind_nonpooled = []
        elif cluster_slices is not None:
            nonpooled_shape = np.array(null.shape)[nonpooled_dims]
            c = _get_max_cluster_per_dim(cluster_slices,
                                         cluster_stats,
                                         nonpooled_dims,
                                         nonpooled_shape)

            cluster_stats_nonpooled, cluster_ind_nonpooled = c
        else:
            cluster_stats_nonpooled = np.zeros(null.shape[slice(*nonpooled_dims)])
            cluster_ind_nonpooled = []

        if ret_clusters:
            clusts = (cluster_slices, cluster_stats, cluster_ind_nonpooled)
            return cluster_stats_nonpooled, clusts
        else:
            return cluster_stats_nonpooled

    def get_obs_clusters(self, data):

        f = self.fit_class(self._design, data)
        if len(self.tstat_args) != 0 and self.perm_metric == 'tstats':
            # Use defaults
            metric = f.get_tstats(**self.tstat_args)
        else:
            metric = getattr(f, self.perm_metric)
        metric = metric[self.contrast_idx, ...]

        cluster_masks, cluster_stats = self._extract_clusters(metric)

        return cluster_masks, cluster_stats

    def get_sig_clusters(self, data, thresh):

        pooled_dims = np.array(self.pooled_dims) - 1

        c = self.get_obs_clusters(data)
        cluster_masks, cluster_stats = c

        if cluster_masks is None:
            return None, None

        thresh = self.get_thresh(thresh)

        sig_inds = []
        for c in range(len(cluster_stats)):
            clust_nonpooled_inds = np.sum(cluster_masks == c + 1,
                                          axis=tuple(pooled_dims)) > 0
            if isinstance(thresh, (int, float)):
                if self.tail == 1:
                    if cluster_stats[c] > thresh:
                        sig_inds.append(c)
                elif self.tail == -1:
                    if cluster_stats[c] < -thresh:
                        sig_inds.append(c)
                elif self.tail == 0:
                    if np.abs(cluster_stats[c]) > thresh:
                        sig_inds.append(c)
            else:
                if self.tail == 1:
                    if cluster_stats[c] > thresh[clust_nonpooled_inds]:
                        sig_inds.append(c)
                elif self.tail == -1:
                    if cluster_stats[c] < thresh[clust_nonpooled_inds]:
                        sig_inds.append(c)
                elif self.tail == 0:
                    if np.abs(cluster_stats[c]) > thresh[clust_nonpooled_inds]:
                        sig_inds.append(c)

        if len(sig_inds) > 0:
            sig_cluster_masks = np.zeros_like(cluster_masks)
            sig_cluster_stats = np.zeros((len(sig_inds,)))

            for c in range(len(sig_inds)):
                sig_cluster_masks[cluster_masks == sig_inds[c] + 1] = c + 1
                sig_cluster_stats[c] = cluster_stats[sig_inds[c]]

            return sig_cluster_masks, sig_cluster_stats
        else:
            return None, None


# Cluster helpers

def _define_connectivity_structure(rank, nonpooled_dims):

    # Create template
    # See ndimage.generate_binary_structure
    q = np.fabs(np.indices([3] * rank) - 1)

    # Assume connectivity distance of 1, might expose this later
    connectivity_dist = 1

    # Set distance for unpooled dims to waay above threshold
    q[nonpooled_dims, ...] *= 5*connectivity_dist

    return np.add.reduce(q, 0) <= connectivity_dist


def _find_clusters(metric, cluster_forming_threshold, nonpooled_dims=[], stat_power=1, tail=0):

    # Get structure connectivity based on pooled dims
    conn = _define_connectivity_structure(metric.ndim, nonpooled_dims)

    # Find some clusters
    if tail == 1:
        labels, num_features = ndimage.label(metric**stat_power > cluster_forming_threshold, conn)
    elif tail == -1:
        labels, num_features = ndimage.label(metric**stat_power < cluster_forming_threshold, conn)
    elif tail == 0:
        labels, num_features = ndimage.label(np.abs(metric**stat_power) > cluster_forming_threshold, conn)

    # Stop here if no clusters are  found
    if num_features == 0:
        #print('no clusters found')
        return None, [0]

    # Convert clusters to slice notation
    #cluster_slices = ndimage.find_objects(labels, num_features)

    # Find magnitude of each cluster
    cluster_stats = ndimage.measurements.sum(metric**stat_power,
                                             labels,
                                             index=np.arange(1, num_features+1))

    return labels, cluster_stats


def _get_max_cluster_per_dim(cluster_slices, cluster_stats, nonpooled_dims, nonpooled_shape):

    # Loop through clusters and save its value in correponding nonpooled dims
    # (if its the biggest in that nonpooled dim)
    cluster_stats_nonpooled = np.zeros(nonpooled_shape)
    cluster_inds_nonpooled = []
    for ii in range(len(cluster_slices)):
        # Get indices of clusterinto nonpooled_dims
        idx = [cluster_slices[ii][np].start for np in nonpooled_dims]
        cluster_inds_nonpooled.append(idx)
        # Assign cluster stat if biggest
        if cluster_stats_nonpooled[idx] < cluster_stats[ii]:
            cluster_stats_nonpooled[idx] = cluster_stats[ii]

    return cluster_stats_nonpooled, cluster_inds_nonpooled


def _get_inds(q, ii):
    """Get location of matching values."""
    return np.where(q[:, ii])[0]


def get_spatial_cluster_inds_from_sensors(x, adj):
    """Get spatial cluster given data and adjacency matrix."""
    q = x[:, None].dot(x[None, :]) * adj

    clu = np.zeros_like(x, dtype=int) - 1
    clust = -1
    for ii in range(q.shape[0]):
        # Are there any significant columns.
        if np.sum(q[:, ii]) > 0:
            # If so where are they?
            inds = np.where(q[:, ii])[0]

            # Skip if already a cluster
            if clu[ii] > -1:
                continue

            # If not a cluster, iteratively expand inds - 5 steps normally enough...
            for jj in range(5):
                inds = np.unique(np.concatenate([_get_inds(q, ii) for ii in inds]))

            clust += 1
            clu[inds] = clust
    return clu


def shakedown_cluster_numbers(c):
    cluster_ids, ccounts = np.unique(c, return_counts=True)
    out = np.zeros_like(c) - 1
    cnt = 0
    for idx, idn in enumerate(cluster_ids):
        if idn == -1:
            continue  # Drop null region
        out[c == idn] = cnt
        cnt += 1
    return out


def get_cluster_extents(x, c, pwr=1):
    cluster_ids = np.unique(c)
    out = np.zeros((len(cluster_ids),))
    for idx, idn in enumerate(cluster_ids):
        if pwr == 0:
            out[idx] = np.sum(c == idn)
        else:
            out[idx] = np.sum(x[c == idn]**pwr)
    return cluster_ids, out


def get_sensor_time_clusters(X, A, cft=5, pwr=1):
    """
    X = [sensors x time]
    A = modality adjacency
    """

    # Get connectivity in time for each sensor
    conn = np.zeros((3, 3))
    conn[:, 1] = True
    C_time = ndimage.label(X > cft, conn.T)[0] - 1

    # Get connectivity in space for each timepoint
    C = np.zeros_like(X)
    clust = -1
    for ii in range(X.shape[1]):
        C[:, ii] = get_spatial_cluster_inds_from_sensors(X[:, ii] > cft, A)

    # Preallocate some stuff
    C3 = np.zeros_like(C_time) - 1
    clust = -1

    # for each time_cluster, find all associated space for each sample
    for ii in range(0, C_time.max()+1):
        # Find inds of time-cluster
        a, b = np.where(C_time == ii)

        # Are any of these inds already a cluster? reuse ID if so
        tmp = np.array([C3[a[idx], b[idx]] for idx in range(len(b))])
        if np.any(tmp > -1):
            targ = np.max(tmp)
        else:
            clust += 1
            targ = clust

        for idx in range(len(b)):
            tmp = C_time[a[idx], b[idx]]

            # original sample is in cluster
            C3[a[idx], b[idx]] = targ

            # all linked space is in cluster
            tmp2 = C[a[idx], b[idx]]
            inds = np.where(C[:, b[idx]] == tmp2)[0]
            C3[inds, b[idx]] = targ
    C3 = shakedown_cluster_numbers(C3)

    cinds, cexts = get_cluster_extents(X, C3, pwr=pwr)

    return C3, cinds, cexts


class MNEClusterPermutation(Permutation):

    def __init__(self, *args, **kwargs):
        self.cluster_forming_threshold = kwargs.pop('cluster_forming_threshold', [])
        self.adjacency = kwargs.pop('adjacency', [])
        super().__init__(*args, **kwargs)

    def _print_info(self):
        super()._print_info()

        msg = '\tComputing clusters across {0} time-points and {1} channels'
        print(msg.format(self.data_dims[1], self.data_dims[2]))

        msg = '\tUsing cluster forming threshold: {0}'.format(self.cluster_forming_threshold)
        print(msg)

        if (self.adjacency is None) or (len(self.adjacency) == 0):
            print("\tNO ADJACENCY INFO FOUND? - check inputs")

    def _get_null_dims(self, dims, **kwargs):
        return (self.nperms,)

    def _extract_perm_stat(self, null, **kwargs):
        from mne.stats.cluster_level import _find_clusters as mne_find_clusters

        flatt = null.flatten()
        clus, cstats = mne_find_clusters(flatt,
                                         self.cluster_forming_threshold,
                                         adjacency=self.adjacency)

        if len(clus) == 0:
            if self.verbose:
                print('No clusters')
            return 0

        if self.verbose:
            print('Found {0} clusters - {1} is largest'.format(len(cstats), np.abs(cstats).max()))

        if len(cstats) == 0:
            return 0
        else:
            return np.abs(cstats).max()

    def get_obs_clusters(self, data, fit=fit.OLSModel):
        from mne.stats.cluster_level import _find_clusters as mne_find_clusters
        from mne.stats.cluster_level import _reshape_clusters as mne_reshape_clusters

        f = fit(self._design, data)
        if self.perm_metric == 'copes':
            obs = getattr(f, self.perm_metric)[self.contrast_idx, ...]
        elif self.perm_metric == 'tstats':
            obs = f.get_tstats(**self.tstat_args)[self.contrast_idx, ...]

        flatt = obs.flatten()
        clus, cstats = mne_find_clusters(flatt,
                                         self.cluster_forming_threshold,
                                         adjacency=self.adjacency)

        clus = mne_reshape_clusters(clus, obs.shape)
        return obs, clus, cstats

    def get_sig_clusters(self, thresh, data):
        if hasattr(thresh, '__len__'):
            if len(thresh) > 1:
                raise ValueError('Can only return cluster for a single threshold')
            else:
                thresh = thresh[0]
        # Find sig clusters
        obs, clusters, cstats = self.get_obs_clusters(data)
        thresh = self.get_thresh([thresh])
        sigs = np.abs(cstats) > thresh
        sig_inds = np.where(sigs)[0]

        # Collate info from sig clusters
        out = []
        for idx in sig_inds:
            clu = clusters[idx]
            pval = stats.percentileofscore(self.nulls, cstats[idx])
            out.append((cstats[idx], pval, clu))

        # Sort from largest to smallest
        I = np.argsort([c[0] for c in out])[::-1]
        out = [out[ii] for ii in I]
        return out, obs


# -----------------------------------------------


def permute_glm(glmdes, data, nperms=5000, stat='cope',
                maxstat_axes=None, stat_corr_mode=None, cluster_forming_threshold=None,
                temporal_varcope_smoothing=None, nprocesses=1, smooth_dims=None):
    """
    Permute rows of design matrix to generate null distributions
    """

    f = fit.OLSModel(glmdes, data)
    data_shape = np.array(data.data.shape)

    null_dim, maxstat_axes, nomaxstat_axes = _get_null_dims(data_shape,
                                                            glmdes.num_contrasts,
                                                            nperms, maxstat_axes)
    nulls = np.zeros(null_dim)

    if maxstat_axes is not None:
        labels = [data.dim_labels[x] for x in np.atleast_1d(maxstat_axes)]
        print('Taking max-stat across {0} dimensions'.format(labels))

    if temporal_varcope_smoothing is not None:
        labels = [data.dim_labels[x] for x in np.atleast_1d(smooth_dims)]
        print('Varcope smoothing across {0} dimensions'.format(labels))

    if stat == 'cope':
        metric = f.copes
    elif stat == 'tstat':
        f.time_dim = 2
        metric = f.get_tstats(temporal_varcope_smoothing=temporal_varcope_smoothing, smooth_dims=smooth_dims)

    nulls[:, 0, ...] = extract_perm_stat(metric, stat_corr_mode,
                                         maxstat_axes=maxstat_axes,
                                         cluster_forming_threshold=cluster_forming_threshold)
    if maxstat_axes is not None:
        maxstat_axes -= 1

    x = glmdes.design_matrix.copy()
    from copy import deepcopy
    g = deepcopy(glmdes)

    # Indices of regressors of interest for each contrast
    cinds = [np.where(glmdes.contrasts[ii, :] != 0.)[0] for ii in range(glmdes.num_contrasts)]

    for jj in range(glmdes.num_contrasts):

        ctype = glmdes.contrast_list[jj].ctype
        rtype = [glmdes.regressor_list[ii].rtype for ii in cinds[jj]]
        rtype = np.unique(rtype)
        if len(rtype) > 1:
            raise ValueError('Contrast is mixing multiple regressor types')
        else:
            rtype = rtype[0]

        mode = None
        if rtype == 'Constant':
            mode = 'sign-flip'
        elif rtype == 'Categorical':
            if ctype == 'Differential':
                mode = 'row-shuffle'
            else:
                mode = 'sign-flip'
        elif rtype == 'Parametric':
            mode = 'row-shuffle'

        if mode is None:
            raise ValueError('unable to determine mode')

        print("Permuting contrast {0} with mode={1}".format(glmdes.contrast_list[jj], mode))

        # Might want to parallelise contrasts rather than perms?
        import multiprocessing as mp
        p = mp.Pool(processes=nprocesses)

        args = [(x, cinds, mode, g, data, maxstat_axes, jj, stat, temporal_varcope_smoothing,
                 smooth_dims, stat_corr_mode, cluster_forming_threshold) for ii in range(1, nperms)]
        res = p.starmap(compute_perm, args)

        nulls[jj, 1:, ...] = np.array(res)

    return nulls


def compute_perm(x, cinds, mode, g, data, maxstat_axes, jj, stat, temporal_varcope_smoothing,
                 smooth_dims, stat_corr_mode, cluster_forming_threshold):

    g.design_matrix = apply_permutation(x.copy(), cinds[jj], mode)

    f = fit.OLSModel(g, data)
    if stat == 'cope':
        null = f.copes[jj, ...]
    elif stat == 'tstat':
        f.time_dim = 2
        null = f.get_tstats(temporal_varcope_smoothing=temporal_varcope_smoothing, smooth_dims=smooth_dims)
    else:
        print('stat not recognised: please use stat=\'cope\' or stat=\'tstat\'')

    null = extract_perm_stat(null, stat_corr_mode,
                             maxstat_axes=maxstat_axes,
                             cluster_forming_threshold=cluster_forming_threshold)

    return null


def extract_perm_stat(metric, stat_corr_mode, maxstat_axes=None, cluster_forming_threshold=None):

    if stat_corr_mode is None:
        return metric
    elif stat_corr_mode == 'maxstat':
        if isinstance(maxstat_axes, int) or np.atleast_1d(maxstat_axes).shape[0] == 1:
            tmp = np.nanmax(np.abs(metric), axis=maxstat_axes)
        elif isinstance(maxstat_axes, np.ndarray):
            tmp = np.nanmax(np.abs(metric), axis=tuple(maxstat_axes))
        return tmp
    elif stat_corr_mode == 'cluster':
        clus, cstat = _find_clusters(metric, threshold=cluster_forming_threshold)
        return cstat.max()
    else:
        raise ValueError("stat_corr_mode: '{0}' not recognised")


def apply_permutation(X, cinds, mode):

    if mode == 'sign-flip':
        perm_inds = np.random.permutation(np.tile([1, -1], int(X.shape[0]/2)))
        X[:, cinds] = X[:, cinds] * perm_inds[:, None]
    elif mode == 'row-shuffle':
        perm_inds = np.random.permutation(X.shape[0])
        ix = np.ix_(perm_inds, cinds)  # np.ix allows us to apply indexing to both dims
        X[:, cinds] = X[ix]

    return X


def _get_null_dims(dims, ncons, nperms, maxstat_axes):

    # everything is an array for sanity
    dims = np.atleast_1d(dims)
    dim_range = np.array(np.arange(len(dims)))
    if maxstat_axes is not None:
        maxstat_axes = np.array(maxstat_axes)

    # First dim is always changed by GLM
    nomaxstat_axes = np.setdiff1d(dim_range[1:], maxstat_axes)

    # Create shape of null
    null_dims = (ncons, nperms, *dims[nomaxstat_axes])

    return null_dims, maxstat_axes, nomaxstat_axes


def _check_false_positives(nperms=2000):
    """ Utility script for a simple false positive rate check.

    This is very noisy so isn't included as a formal test case but is useful to
    make sure that a simple white noise test is giving approximately correct
    false positive rates.  """
    from . import design, data

    A = np.random.randn(100, 500, 5)
    B = np.random.randn(100, 500, 5)

    X = np.r_[A, B]
    categories = np.repeat((1, 2), 100)
    dat = data.TrialGLMData(data=X,
                            category_list=categories,
                            dim_labels=['Trials', 'Voxels', 'Frequencies'])

    dat.dim_labels = dat.info['dim_labels']

    DC = design.DesignConfig()
    DC.add_regressor(name='A', rtype='Categorical', codes=1)
    DC.add_regressor(name='B', rtype='Categorical', codes=2)
    DC.add_contrast(name='GroupDiff', values=[1, -1])

    des = DC.design_from_datainfo(dat.info)

    model = fit.OLSModel(des, dat)

    P = Permutation(des, dat, 0, nperms,
                    metric='tstats', nprocesses=6)

    thresh = P.get_thresh([95, 99, 99.9])

    msg = '{0}/{1} - {2}%'

    print('False positives at alpha=.95')
    pc = (np.sum(model.tstats > thresh[0]) / np.product(model.tstats.shape)) * 100
    print(msg.format(np.sum(model.tstats > thresh[0]),
                     np.product(model.tstats.shape),
                     pc))

    print('False positives at alpha=.99')
    pc = (np.sum(model.tstats > thresh[1]) / np.product(model.tstats.shape)) * 100
    print(msg.format(np.sum(model.tstats > thresh[1]),
                     np.product(model.tstats.shape),
                     pc))

    print('False positives at alpha=.999')
    pc = (np.sum(model.tstats > thresh[2]) / np.product(model.tstats.shape)) * 100
    print(msg.format(np.sum(model.tstats > thresh[2]),
                     np.product(model.tstats.shape),
                     pc))


def _check_false_positives_maxstat(nperms=2000):
    """ Utility script for a simple false positive rate check.

    This is very noisy so isn't included as a formal test case but is useful to
    make sure that a simple white noise test is giving approximately correct
    false positive rates.  """
    from . import design, data

    A = np.random.randn(100, 500, 5)
    B = np.random.randn(100, 500, 5)

    X = np.r_[A, B]
    categories = np.repeat((1, 2), 100)
    dat = data.TrialGLMData(data=X,
                            category_list=categories,
                            dim_labels=['Trials', 'Voxels', 'Frequencies'])

    dat.dim_labels = dat.info['dim_labels']

    DC = design.DesignConfig()
    DC.add_regressor(name='A', rtype='Categorical', codes=1)
    DC.add_regressor(name='B', rtype='Categorical', codes=2)
    DC.add_contrast(name='GroupDiff', values=[1, -1])

    des = DC.design_from_datainfo(dat.info)

    model = fit.OLSModel(des, dat)

    P = MaxStatPermutation(des, dat, 0, nperms, pooled_dims=(1, 2),
                           metric='tstats', nprocesses=6)

    thresh = P.get_thresh([95, 99, 99.9])

    msg = '{0}/{1} - {2}%'

    print('False positives at alpha=.95')
    pc = (np.sum(model.tstats > thresh[0]) / np.product(model.tstats.shape)) * 100
    print(msg.format(np.sum(model.tstats > thresh[0]),
                     np.product(model.tstats.shape),
                     pc))

    print('False positives at alpha=.99')
    pc = (np.sum(model.tstats > thresh[1]) / np.product(model.tstats.shape)) * 100
    print(msg.format(np.sum(model.tstats > thresh[1]),
                     np.product(model.tstats.shape),
                     pc))

    print('False positives at alpha=.999')
    pc = (np.sum(model.tstats > thresh[2]) / np.product(model.tstats.shape)) * 100
    print(msg.format(np.sum(model.tstats > thresh[2]),
                     np.product(model.tstats.shape),
                     pc))


def c_corrected_permute_glm(glmdes, data, nperms=5000, nomax_axis=None,
                            temporal_varcope_smoothing=None, threshold=3):
    """
    Permute rows of design matrix to generate null distributions of clusters

    """
    # Null creation just contrasts x permutations
    nulls = np.zeros((glmdes.num_contrasts, nperms))

    x = glmdes.design_matrix.copy()
    from copy import deepcopy
    g = deepcopy(glmdes)

    # Indices of regressors of interest for each contrast
    cinds = [np.where(glmdes.contrasts[ii, :] != 0.)[0] for ii in range(glmdes.num_contrasts)]

    for jj in range(glmdes.num_contrasts):

        ctype = glmdes.contrast_list[jj].ctype
        rtype = [glmdes.regressor_list[ii].rtype for ii in cinds[jj]]
        rtype = np.unique(rtype)
        if len(rtype) > 1:
            raise ValueError('Contrast is mixing multiple regressor types')
        else:
            rtype = rtype[0]

        mode = None
        if rtype == 'Categorical':
            if ctype == 'Differential':
                mode = 'row-shuffle'
            else:
                mode = 'sign-flip'
        elif rtype == 'Parametric':
            mode = 'row-shuffle'
        elif rtype == 'Continous':
            mode = 'row-shuffle'

        if mode is None:
            raise ValueError('unable to determine mode')

        print('Permuting {0} by {1}'.format(glmdes.contrast_list[jj], mode))
        for ii in range(0, nperms):

            perc_done = ii/nperms

            sys.stdout.write("\rClustering %i percent" % round(perc_done * 100, 2))
            sys.stdout.flush()

            g.design_matrix = apply_permutation(x.copy(), cinds[jj], mode)

            f = fit.OLSModel(g, data)
            tstats = f.get_tstats(temporal_varcope_smoothing=temporal_varcope_smoothing)

            # get clusters
            clus, cstat = _find_clusters(tstats[jj], threshold=threshold)

            nulls[jj, ii] = cstat.max()

    return nulls
