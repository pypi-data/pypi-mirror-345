import numpy as np
from .intense_base import calculate_optimal_delays_parallel, calculate_optimal_delays, scan_pairs, scan_pairs_parallel
from ..information.info_base import TimeSeries

ts_bunch1 = [TimeSeries(np.random.random(size=10000)) for _ in range(12)]
ts_bunch2 = [TimeSeries(np.random.random(size=10000)) for _ in range(20)]
shift_window = 40
ds = 5

optd = np.random.randint(-40, 40, size=(12, 20))

rshifts1, mitable1 = scan_pairs(ts_bunch1,
                                ts_bunch2,
                                100,
                                optd,
                                ds=5,
                                joint_distr=False,
                                noise_const=1e-4,
                                seed=42)

rshifts2, mitable2 = scan_pairs_parallel(ts_bunch1,
                                         ts_bunch2,
                                         100,
                                         optd,
                                         ds=5,
                                         joint_distr=False,
                                         n_jobs=-1,
                                         noise_const=1e-4,
                                         seed=42)

print(rshifts1.shape)
print(rshifts2.shape)
print(np.allclose(rshifts1, rshifts2))
print(np.allclose(mitable1, mitable2))


