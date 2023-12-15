import numpy as np

from pyeuv.SourcePerformance.ctxt_filter_tool import ContextFilterObject


# Create Context Filter Object
dt_vector = np.array([np.datetime64('2020-08-11T17:11:11') + np.timedelta64(i, 'm') for i in np.arange(12,52,2)])
boolean = np.array([0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0])
cfo = ContextFilterObject(dt_vector, boolean)


# Modify Context Filter Object
## Deglitching (inter gate)
dt_vector = np.array([np.datetime64('2020-08-11T17:11:11') + np.timedelta64(i, 'm') for i in np.arange(12,52,2)])
boolean = np.array([0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0])
cfo = ContextFilterObject(dt_vector, boolean)
cfo.deglitch_inter_gates(timedelta_diff=5, inter=False, unit='m')

## Shifting
dt_vector = np.array([np.datetime64('2020-08-11T17:11:11') + np.timedelta64(i, 'm') for i in[5, 10, 15, 18, 20, 30, 35, 37, 45, 55]])
boolean = np.array([1, 0, 1, 0, 1, 0, 1, 0, 1, 0])
cfo = ContextFilterObject(dt_vector, boolean)
cfo.shift_edge_points(timedelta_assert=-2, timedelta_deassert=1, unit='m')

## NOT
dt_vector = np.array([np.datetime64('2020-08-11T17:11:11') + np.timedelta64(i, 'm') for i in [5, 10, 15, 18, 20, 30, 35, 37, 45, 55]])
boolean = np.array([1, 0, 1, 0, 1, 0, 1, 0, 1, 0])
cfo = ContextFilterObject(dt_vector, boolean)
cfo = cfo.not_ctxt_filters()

## Limit frequency of gates (from start)
dt_vector = np.array([np.datetime64('2020-08-11T17:11:11') + np.timedelta64(i, 'm') for i in 		np.arange(3,63,3)])
boolean = np.array([0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0])
cfo = ContextFilterObject(dt_vector, boolean)
cfo.limit_gate_freq(timedelta_diff=30, unit='m', from_end=False)


# Combination of Context Filter Objects
dt_vector_A = np.array([np.datetime64('2020-08-11T17:11:11') + np.timedelta64(i, 'm') for i in np.arange(3,63,3)])
boolean_A = np.array([0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0])
dt_vector_B = np.array([np.datetime64('2020-08-11T17:11:11') + np.timedelta64(i, 'm') for i in [5, 10, 15, 18, 20, 30, 35, 37, 45, 55]])
boolean_B = np.array([1, 0, 1, 0, 1, 0, 1, 0, 1, 0])
cfo_A = ContextFilterObject(dt_vector_A, boolean_A)
cfo_B = ContextFilterObject(dt_vector_B, boolean_B)

## AND
cfo_and = cfo_A.combine_ctxt_filters(cfo2=cfo_B, logic='and')

## OR
cfo_or = cfo_A.combine_ctxt_filters(cfo2=cfo_B, logic='or')

## XOR
cfo_xor = cfo_A.combine_ctxt_filters(cfo2=cfo_B, logic='xor')


# Application of Context Filter Object
## Filter
date_time = np.datetime64('2020-08-11T17:11:11')
dt_vector = np.array([date_time + np.timedelta64(i, 'm') for i in np.arange(12,52,2)])
boolean = np.array([0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0])
cfo = ContextFilterObject(dt_vector, boolean)
filter_dt_vector = np.array([date_time + np.timedelta64(i, 'm') for i in np.arange(0,63,3)])
ramp_signal = np.array([i for i in range(1, len(filter_dt_vector) + 1)])
idx = cfo.apply_ctxt_filter(filter_dt_vector)
ramp_signal_filt = ramp_signal[idx.astype(bool)]


## Aggregate
### Standard
date_time = np.datetime64('2020-08-11T17:11:11')
dt_vector = np.array([date_time + np.timedelta64(i, 'm') for i in [5, 10, 15, 18, 20, 30, 35, 37, 45, 55]])
boolean = np.array([1, 0, 1, 0, 1, 0, 1, 0, 1, 0])
cfo = ContextFilterObject(dt_vector, boolean)
filter_dt_vector = np.array([date_time + np.timedelta64(i, 'm') for i in np.arange(0,63,3)])
all_one = np.ones(len(filter_dt_vector))
time_aggr_sum, data_aggr_sum = cfo.agg_ctxt_filter(filter_dt_vector, all_one, lambda x: np.sum(x))

### User function
ramp_signal = np.array([i for i in range(1, len(filter_dt_vector) + 1)])
time_aggr_maxmin, data_aggr_maxmin = cfo.agg_ctxt_filter(filter_dt_vector, ramp_signal, lambda x: np.max(x) - np.min(x))
