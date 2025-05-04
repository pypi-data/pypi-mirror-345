from .driada.experiment.exp_build import load_experiment
from ..experiment.neuron import DEFAULT_FPS, DEFAULT_T_OFF, DEFAULT_T_RISE
from ..intense.pipelines import compute_cell_feat_mi_significance

exp_params = {
    'track': 'HT',
    'animal_id': 'CA1_22',
    'session': 3
}

default_static_features = {'t_rise_sec': DEFAULT_T_RISE,
                           't_off_sec': DEFAULT_T_OFF,
                           'fps': DEFAULT_FPS}

Exp = load_experiment('IABS',
                      exp_params,
                      force_reload=True,
                      root='DRIADA data',
                      force_continuous=['x', 'y', 'v'],
                      static_features=None)


comp_stats, comp_sign = compute_cell_feat_mi_significance(Exp,
                                                          cell_bunch=None,
                                                          feat_bunch=None,
                                                          mode='two_stage',
                                                          n_shuffles_stage1=100,
                                                          n_shuffles_stage2=100,
                                                          joint_distr=False,
                                                          mi_distr_type='gamma',
                                                          noise_ampl=1e-3,
                                                          ds=5,
                                                          use_precomputed_stats=True,
                                                          save_computed_stats=True,
                                                          force_update=False,
                                                          topk1=1,
                                                          topk2=5,
                                                          multicomp_correction='holm',
                                                          pval_thr=0.01,
                                                          verbose=True)

