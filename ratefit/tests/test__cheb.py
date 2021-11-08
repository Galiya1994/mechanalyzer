""" Tests the Chebyshev fitter
"""

import numpy
from ratefit.fit import cheb
from ratefit.fit import err


# Data to fit
TEMPS = numpy.arange(300.0, 2500, 100.0)  # only goes up to 2400
KTP_DCT = {
    0.1: (TEMPS, numpy.array(
        [1.08450103e-06, 4.02056587e-02, 2.67879037e+01, 2.18532255e+03,
         4.53398238e+04, 3.60139663e+05, 1.45018006e+06, 3.60988324e+06,
         6.38901400e+06, 8.87215267e+06, 1.03634259e+07, 1.06987289e+07,
         1.01130485e+07, 8.97902728e+06, 7.62804534e+06, 6.28500509e+06,
         5.07244048e+06, 4.03946844e+06, 3.19135182e+06, 2.51133072e+06,
         1.97421057e+06, 1.55376775e+06])),
    1.0: (TEMPS, numpy.array(
        [1.05204297e-06, 4.37287193e-02, 2.68683407e+01, 2.33553171e+03,
         6.11167966e+04, 6.64960593e+05, 3.74422528e+06, 1.28835884e+07,
         3.07244837e+07, 5.57883099e+07, 8.26967252e+07, 1.05371941e+08,
         1.19913201e+08, 1.25396286e+08, 1.23093791e+08, 1.15262582e+08,
         1.04210676e+08, 9.18153940e+07, 7.93887558e+07, 6.77312296e+07,
         5.72544387e+07, 4.81070825e+07])),
    5.0: (TEMPS, numpy.array(
        [1.03195059e-06, 4.51888681e-02, 2.58346404e+01, 2.19539776e+03,
         6.18976976e+04, 7.74446059e+05, 5.18193172e+06, 2.14400511e+07,
         6.14663642e+07, 1.33290864e+08, 2.33700127e+08, 3.48414202e+08,
         4.58824325e+08, 5.49334987e+08, 6.11221003e+08, 6.42712213e+08,
         6.46985110e+08, 6.29740256e+08, 5.97285483e+08, 5.55368956e+08,
         5.08649782e+08, 4.60589012e+08])),
    10.0: (TEMPS, numpy.array(
        [1.02854867e-06, 4.54462673e-02, 2.55882776e+01, 2.14313125e+03,
         6.09581958e+04, 7.87229443e+05, 5.52751500e+06, 2.42486903e+07,
         7.41295252e+07, 1.71833810e+08, 3.22150011e+08, 5.13016160e+08,
         7.20276630e+08, 9.17230565e+08, 1.08265014e+09, 1.20439945e+09,
         1.27916208e+09, 1.31010944e+09, 1.30413070e+09, 1.26952728e+09,
         1.21446106e+09, 1.14609891e+09])),
    20.0: (TEMPS, numpy.array(
        [1.03006701e-06, 4.54387780e-02, 2.56341148e+01, 2.12010613e+03,
         5.99626704e+04, 7.83171633e+05, 5.65725653e+06, 2.58820537e+07,
         8.33172377e+07, 2.04648252e+08, 4.08031125e+08, 6.92217829e+08,
         1.03569539e+09, 1.40463446e+09, 1.76350702e+09, 2.08321497e+09,
         2.34488271e+09, 2.53997245e+09, 2.66829042e+09, 2.73529370e+09,
         2.74957776e+09, 2.72093196e+09])),
    50.0: (TEMPS, numpy.array(
        [1.04183916e-06, 4.49835129e-02, 2.63629986e+01, 2.16291378e+03,
         5.93540953e+04, 7.59794305e+05, 5.50077721e+06, 2.58129437e+07,
         8.69088124e+07, 2.26620973e+08, 4.84815568e+08, 8.88840854e+08,
         1.44354631e+09, 2.13010602e+09, 2.91213575e+09, 3.74488944e+09,
         4.58379302e+09, 5.39036895e+09, 6.13522323e+09, 6.79867258e+09,
         7.36986370e+09, 7.84514937e+09])),
    100.0: (TEMPS, numpy.array(
        [1.06001201e-06, 4.42811270e-02, 2.76274082e+01, 2.27730457e+03,
         6.00191004e+04, 7.34814182e+05, 5.16987678e+06, 2.40869598e+07,
         8.21693105e+07, 2.20782995e+08, 4.93093215e+08, 9.52892469e+08,
         1.64235752e+09, 2.58362271e+09, 3.77615383e+09, 5.19915635e+09,
         6.81694453e+09, 8.58518980e+09, 1.04565997e+10, 1.23853058e+10,
         1.43297921e+10, 1.62545195e+10]))}

# Params used for fitting
TDEG, PDEG = 6, 4


def test_cheb():
    """ test ratefit.fit.chebyshev.reaction
    """

    ref_alpha = numpy.array(
        [[1.86421309e+00, 4.20602838e-01, -5.74358452e-02, -5.45222311e-05],
         [7.61423648e+00, 7.51012552e-01, -9.23375204e-02, -8.25427040e-03],
         [-4.89211391e-01, 5.10360005e-01, -2.71105409e-02, -1.04075446e-02],
         [-3.93397030e-01, 2.67821927e-01, 1.58876205e-02, -6.32223880e-03],
         [-2.15290577e-01, 7.79192168e-02, 4.05605101e-02, 3.99721924e-03],
         [-8.40067735e-02, -2.24969601e-03, 2.50720909e-02, 5.36853083e-03]])
    ref_tmin = 300
    ref_tmax = 2400
    ref_pmin = 0.1
    ref_pmax = 100

    params, err_dct = cheb.get_params(KTP_DCT, tdeg=TDEG, pdeg=PDEG)

    assert numpy.allclose(params.cheb['alpha'], ref_alpha)
    assert numpy.allclose(params.cheb['tlim'], (ref_tmin, ref_tmax))
    assert numpy.allclose(params.cheb['plim'], (ref_pmin, ref_pmax))

    max_err = err.get_max_err(err_dct)
    assert max_err < 5


if __name__ == '__main__':
    test_cheb()
