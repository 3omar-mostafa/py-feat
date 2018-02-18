#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `feat` package."""

import pytest
import pandas as pd
import numpy as np
from os.path import join, exists
from .utils import get_test_data_path
from feat.data import Fex, Facet, Openface
from feat.utils import read_facet, read_openface
from nltools.data import Adjacency
import unittest

def test_fex(tmpdir):
    # For iMotions-FACET data files
    # test reading iMotions file < version 6
    dat = Fex(read_facet(join(get_test_data_path(), 'iMotions_Test_v2.txt')), sampling_freq=30)

    # test reading iMotions file > version 6
    filename = join(get_test_data_path(), 'iMotions_Test.txt')
    df = read_facet(filename)
    sessions = np.array([[x]*10 for x in range(1+int(len(df)/10))]).flatten()[:-1]
    dat = Fex(df, sampling_freq=30, sessions=sessions)

    # Test KeyError
    class MyTestCase(unittest.TestCase):
        def test1(self):
            with self.assertRaises(KeyError):
                Fex(read_facet(filename, features=['NotHere']), sampling_freq=30)

    # Test length
    assert len(dat)==519

    # Test Info
    assert isinstance(dat.info(), str)

    # Test sessions generator
    assert len(np.unique(dat.sessions))==len([x for x in dat.itersessions()])

    # Test metadata propagation
    assert dat['Joy'].sampling_freq == dat.sampling_freq
    assert dat.iloc[:,0].sampling_freq == dat.sampling_freq

    # Test Downsample
    assert len(dat.downsample(target=10))==52

    # Test upsample
    assert len(dat.upsample(target=60,target_type='hz'))==(len(dat)-1)*2

    # Test interpolation
    assert np.sum(dat.interpolate(method='linear').isnull().sum()==0) == len(dat.columns)
    dat = dat.interpolate(method='linear')

    # Test distance
    d = dat.distance()
    assert isinstance(d, Adjacency)
    assert d.square_shape()[0]==len(dat)

    # Test Copy
    assert isinstance(dat.copy(), Fex)
    assert dat.copy().sampling_freq==dat.sampling_freq

    # Test baseline
    assert isinstance(dat.baseline(baseline='median'), Fex)
    assert isinstance(dat.baseline(baseline='mean'), Fex)
    assert isinstance(dat.baseline(baseline=dat.mean()), Fex)
    assert isinstance(dat.baseline(baseline='median', ignore_sessions=True), Fex)
    assert isinstance(dat.baseline(baseline='mean', ignore_sessions=True), Fex)
    assert isinstance(dat.baseline(baseline=dat.mean(), ignore_sessions=True), Fex)
    assert isinstance(dat.baseline(baseline='median', normalize='pct'), Fex)
    assert isinstance(dat.baseline(baseline='mean', normalize='pct'), Fex)
    assert isinstance(dat.baseline(baseline=dat.mean(), normalize='pct'), Fex)
    assert isinstance(dat.baseline(baseline='median', ignore_sessions=True, normalize='pct'), Fex)
    assert isinstance(dat.baseline(baseline='mean', ignore_sessions=True, normalize='pct'), Fex)
    assert isinstance(dat.baseline(baseline=dat.mean(), ignore_sessions=True, normalize='pct'), Fex)

    # Test extract_max
    dat_max = dat.extract_max(ignore_sessions=False)
    assert isinstance(dat_max, Fex)
    assert dat_max.sampling_freq==dat.sampling_freq
    assert len(dat_max) ==len(np.unique(dat.sessions))
    dat_max = dat.extract_max(ignore_sessions=True)
    assert len(dat_max)==1
    assert dat_max.shape[1]==dat.shape[1]
    assert dat_max.sampling_freq==dat.sampling_freq

    # Test extract_min
    dat_min = dat.extract_min(ignore_sessions=False)
    assert isinstance(dat_min, Fex)
    assert dat_min.sampling_freq==dat.sampling_freq
    assert len(dat_min) ==len(np.unique(dat.sessions))
    dat_min = dat.extract_min(ignore_sessions=True)
    assert len(dat_min)==1
    assert dat_min.shape[1]==dat.shape[1]
    assert dat_min.sampling_freq==dat.sampling_freq

    # Test extract_mean
    dat_mean = dat.extract_mean(ignore_sessions=False)
    assert isinstance(dat_mean, Fex)
    assert dat_mean.sampling_freq==dat.sampling_freq
    assert len(dat_mean) ==len(np.unique(dat.sessions))
    dat_mean = dat.extract_mean(ignore_sessions=True)
    assert len(dat_mean)==1
    assert dat_mean.shape[1]==dat.shape[1]
    assert dat_mean.sampling_freq==dat.sampling_freq

    # Test summary
    dat2 = dat.loc[:,['Positive','Negative']].interpolate()
    out = dat2.extract_summary(min=True, max=True, mean=True)
    assert len(out) == len(np.unique(dat2.sessions))
    assert np.array_equal(out.sessions, np.unique(dat2.sessions))
    assert out.sampling_freq == dat2.sampling_freq
    assert dat2.shape[1]*3 == out.shape[1]

    # Test facet subclass
    facet = Facet(filename=filename,sampling_freq=30)
    facet.read_file()
    assert len(facet)==519

    # Test PSPI calculation
    assert len(facet.calc_pspi()) == len(facet)

    # Test wavelet
    dat = dat.interpolate()
    f = .5; num_cyc=3
    wavelet = dat.extract_wavelet(freq=f, num_cyc=num_cyc, ignore_sessions=True)
    assert wavelet.sampling_freq == dat.sampling_freq
    assert len(wavelet) == len(dat)
    wavelet = dat.extract_wavelet(freq=f, num_cyc=num_cyc, ignore_sessions=False)
    assert wavelet.sampling_freq == dat.sampling_freq
    assert len(wavelet) == len(dat)
    assert np.array_equal(wavelet.sessions,dat.sessions)
    for i in ['filtered','phase','magnitude','power']:
        wavelet = dat.extract_wavelet(freq=f, num_cyc=num_cyc, ignore_sessions=True, mode=i)
        assert wavelet.sampling_freq == dat.sampling_freq
        assert len(wavelet) == len(dat)

    # Test multi wavelet
    dat2 = dat.loc[:,['Positive','Negative']].interpolate()
    n_bank=4
    out = dat2.extract_multi_wavelet(min_freq=.1, max_freq=2, bank=n_bank, mode='power', ignore_sessions=False)
    assert n_bank * dat2.shape[1] == out.shape[1]
    assert len(out) == len(dat2)
    assert np.array_equal(out.sessions, dat2.sessions)
    assert out.sampling_freq == dat2.sampling_freq

    # Test Bag Of Temporal Features Extraction
    facet_filled = facet.fillna(0)
    # assert isinstance(facet_filled,Facet)
    # assert isinstance(facet_filled.extract_boft(), Facet)
    # filters, histograms = 8, 12
    # assert facet_filled.extract_boft().shape[1]==facet.columns.shape[0] * filters * histograms

    # Test mean, min, and max Features Extraction
    # assert isinstance(facet_filled.extract_mean(), Facet)
    # assert isinstance(facet_filled.extract_min(), Facet)
    # assert isinstance(facet_filled.extract_max(), Facet)

    # Test if a method returns subclass.
    facet = facet.downsample(target=10,target_type='hz')
    assert isinstance(facet,Facet)

    ### Test Openface importer and subclass ###

    # For OpenFace data file
    filename = join(get_test_data_path(), 'OpenFace_Test.csv')
    openface = Fex(read_openface(filename), sampling_freq=30)

    # Test KeyError
    class MyTestCase(unittest.TestCase):
        def test1(self):
            with self.assertRaises(KeyError):
                Fex(read_openface(filename, features=['NotHere']), sampling_freq=30)

    # Test length
    assert len(openface)==100

    # Test loading from filename
    openface = Openface(filename=filename, sampling_freq = 30)
    openface.read_file()

    # Test length?
    assert len(openface)==100

    # Test PSPI calculation b/c diff from facet
    assert len(openface.calc_pspi()) == len(openface)

    # Test if a method returns subclass.
    openface = openface.downsample(target=10,target_type='hz')
    assert isinstance(openface,Openface)

    # Check if file is missing columns
    data_bad = dat.iloc[:,0:10]
    with pytest.raises(Exception):
        _check_if_fex(data_bad, imotions_columns)

    # Check if file has too many columns
    data_bad = dat.copy()
    data_bad['Test'] = 0
    with pytest.raises(Exception):
        _check_if_fex(data_bad, imotions_columns)

    # Test clean
    assert isinstance(dat.clean(), Fex)
    assert dat.clean().columns is dat.columns
    assert dat.clean().sampling_freq == dat.sampling_freq

    # Test Decompose
    n_components = 3
    stats = dat.decompose(algorithm='pca', axis=1,
                          n_components=n_components)
    assert n_components == stats['components'].shape[1]
    assert n_components == stats['weights'].shape[1]

    stats = dat.decompose(algorithm='ica', axis=1,
                          n_components=n_components)
    assert n_components == stats['components'].shape[1]
    assert n_components == stats['weights'].shape[1]

    new_dat = dat+100
    stats = new_dat.decompose(algorithm='nnmf', axis=1,
                              n_components=n_components)
    assert n_components == stats['components'].shape[1]
    assert n_components == stats['weights'].shape[1]

    stats = dat.decompose(algorithm='fa', axis=1,
                          n_components=n_components)
    assert n_components == stats['components'].shape[1]
    assert n_components == stats['weights'].shape[1]

    stats = dat.decompose(algorithm='pca', axis=0,
                          n_components=n_components)
    assert n_components == stats['components'].shape[1]
    assert n_components == stats['weights'].shape[1]

    stats = dat.decompose(algorithm='ica', axis=0,
                          n_components=n_components)
    assert n_components == stats['components'].shape[1]
    assert n_components == stats['weights'].shape[1]

    new_dat = dat+100
    stats = new_dat.decompose(algorithm='nnmf', axis=0,
                              n_components=n_components)
    assert n_components == stats['components'].shape[1]
    assert n_components == stats['weights'].shape[1]

    stats = dat.decompose(algorithm='fa', axis=0,
                          n_components=n_components)
    assert n_components == stats['components'].shape[1]
    assert n_components == stats['weights'].shape[1]
