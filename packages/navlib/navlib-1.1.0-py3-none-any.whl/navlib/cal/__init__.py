# import methods from the corresponding modules
from .cal_ahrs import cal_ahrs_so3
from .cal_dvl import cal_dvl_acc_so3, cal_dvl_correct_by_sound_velocity, cal_dvl_jck_so3
from .cal_mag import (
    cal_mag_ellipsoid_fit,
    cal_mag_ellipsoid_fit_fang,
    cal_mag_magfactor3,
    cal_mag_magyc_bfg,
    cal_mag_magyc_ifg,
    cal_mag_magyc_ls,
    cal_mag_magyc_nls,
    cal_mag_sar_aid,
    cal_mag_sar_kf,
    cal_mag_sar_ls,
    cal_mag_sphere_fit,
    cal_mag_twostep_hi,
    cal_mag_twostep_hsi,
)

# Get __all__ from the corresponding modules
__all__ = ["cal_ahrs_so3"]
__all__ += ["cal_dvl_acc_so3", "cal_dvl_correct_by_sound_velocity", "cal_dvl_jck_so3"]
__all__ += [
    "cal_mag_ellipsoid_fit",
    "cal_mag_ellipsoid_fit_fang",
    "cal_mag_magfactor3",
    "cal_mag_twostep_hi",
    "cal_mag_twostep_hsi",
    "cal_mag_sphere_fit",
    "cal_mag_sar_ls",
    "cal_mag_sar_kf",
    "cal_mag_sar_aid",
    "cal_mag_magyc_ls",
    "cal_mag_magyc_nls",
    "cal_mag_magyc_bfg",
    "cal_mag_magyc_ifg",
]
