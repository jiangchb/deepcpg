import numpy as np
import h5py as h5
import os.path as pt

import predict.utils as ut


def sort_cpos(d):
    for k, v in d.items():
        d[k] = np.asarray(v)
    dc = {k: v.copy() for k, v in d.items()}
    chromos = np.unique(d['chromo'])
    chromos.sort()
    i = 0
    for chromo in chromos:
        h = d['chromo'] == chromo
        j = i + h.sum()
        for k, v in d.items():
            dc[k][i:j] = v[h]
        h = np.argsort(dc['pos'][i:j])
        for k, v in dc.items():
            dc[k][i:j] = dc[k][i:j][h]
        i = j
    return dc


def cpos_to_list(chromos, pos):
    _chromos = np.unique(np.asarray(chromos))
    _pos = []
    for c in _chromos:
        _pos.append(pos[chromos == c])
    return (_chromos, _pos)


def cpos_to_vec(chromos, pos):
    _chromos = []
    for i, p in enumerate(pos):
        _chromos.append([chromos[i]] * len(p))
    _chromos = np.hstack(_chromos)
    _pos = np.hstack(pos)
    return (_chromos, _pos)


def _read_stats(path, chromo, names, pos=None):
    f = h5.File(path, 'r')
    g = f[str(chromo)]
    p = g['pos'].value
    if not isinstance(names, list):
        names = [names]
    d = np.vstack([g[x].value for x in names]).T
    f.close()
    if pos is not None:
        t = np.in1d(p, pos)
        d = d[t]
        p = p[t]
        assert np.all(p == pos)
    return p, d


def read_stats(path, chromos=None, pos=None, regex=None):
    f = h5.File(path, 'r')
    if chromos is None:
        chromos = list(f.keys())
    elif isinstance(chromos, str):
        chromos = [chromos]
    chromos = [str(x) for x in chromos]
    names = [x for x in f[chromos[0]] if x != 'pos']
    if regex is not None:
        names = ut.filter_regex(names, regex)
    ds = []
    ps = []
    for i, chromo in enumerate(chromos):
        cpos = None
        if pos is not None:
            cpos = pos[i]
        p, d = _read_stats(path, chromo, names, cpos)
        ps.append(p)
        ds.append(d)
    ds = np.vstack(ds)
    return (chromos, ps, ds, names)


def _read_annos(path, chromo, names, pos=None):
    if not isinstance(names, list):
        names = [names]
    f = h5.File(path, 'r')
    p = None
    a = []
    for name in names:
        g = f[pt.join(chromo, name)]
        h = g['pos'].value
        if p is None:
            p = h
        else:
            assert np.all(p == h)
        a.append(g['annos'].value)
    a = np.vstack(a).T
    f.close()
    if pos is not None:
        t = np.in1d(p, pos)
        p = p[t]
        a = a[t]
        assert np.all(p == pos)
    a[a >= 0] = 1
    a[a < 0] = 0
    a = a.astype('bool')
    return (p, a)


def read_annos(path, chromos=None, pos=None, regex=None):
    f = h5.File(path, 'r')
    if chromos is None:
        chromos = list(f.keys())
    elif isinstance(chromos, str):
        chromos = [chromos]
    chromos = [str(x) for x in chromos]
    names = [x for x in f[chromos[0]] if x != 'pos']
    if regex is not None:
        names = ut.filter_regex(names, regex)
    ds = []
    ps = []
    for i, chromo in enumerate(chromos):
        cpos = None
        if pos is not None:
            cpos = pos[i]
        p, d = _read_annos(path, chromo, names, cpos)
        ps.append(p)
        ds.append(d)
    ds = np.vstack(ds)
    return (chromos, ps, ds, names)