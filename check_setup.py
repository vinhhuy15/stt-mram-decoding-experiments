import sys
sys.path.insert(0, '.')
import config
import numpy as np
from simulation import simulate, save_results, load_results
from decoders import soft_decode
import os

def dummy_decoder(received, **ctx):
    return soft_decode(received, alpha=ctx['alpha'])

np.random.seed(0)
r = simulate(n_frames=500, P1=2e-4, sigma_ratio=0.09, alpha=2.5,
             batch=500, custom_decoder=dummy_decoder)

assert 'BER_custom' in r, 'BER_custom key missing!'
assert 'FER_custom' in r, 'FER_custom key missing!'
print('custom_decoder hook: OK')
print('  BER_soft=%s  BER_custom=%s' % (r['BER_soft'], r['BER_custom']))

save_results('results/test_save.npz', x=np.array([1, 2, 3]), y=np.array([0.1, 0.2]))
data = load_results('results/test_save.npz')
assert list(data['x']) == [1, 2, 3]
print('save_results / load_results: OK')

os.remove('results/test_save.npz')
print('All checks passed!')
