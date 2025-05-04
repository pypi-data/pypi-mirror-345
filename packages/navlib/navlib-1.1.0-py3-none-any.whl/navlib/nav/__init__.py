# import methods from the corresponding modules
from .attitude_estimation import (
    ahrs_complementary_filter,
    ahrs_correct_magfield,
    ahrs_hua_mahony_filter,
    ahrs_madgwick_filter,
    ahrs_mahony_filter,
    ahrs_raw_hdg,
    ahrs_raw_rp,
    ahrs_raw_rph,
    so3_integrator,
)
from .kalman_filter import UUV_EKF, kf_lti_discretize, kf_predict, kf_update
from .state_estimation import navdvl_dead_reckoning, navdvl_kf

# Get __all__ from the corresponding modules
# Attitude estimation methods
__all__ = [
    "so3_integrator",
    "ahrs_correct_magfield",
    "ahrs_raw_rp",
    "ahrs_raw_hdg",
    "ahrs_raw_rph",
    "ahrs_complementary_filter",
    "ahrs_mahony_filter",
    "ahrs_hua_mahony_filter",
    "ahrs_madgwick_filter",
]
# Kalman filter methods
__all__ += [
    "kf_lti_discretize",
    "kf_predict",
    "kf_update",
    "UUV_EKF",
]
# State estimation methods
__all__ += [
    "navdvl_dead_reckoning",
    "navdvl_kf",
]
