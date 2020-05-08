"""
Functions to handle various aspects of pressure dependence
"""

import numpy as np


def assess_pressure_dependence(tk_dct, assess_pdep_temps,
                               tolerance=20.0, plow=None, phigh=None):
    """ Assess how much the rate constants change from
        a low-pressure to high-pressure regime

        tk_dct[pressure] = [temps, k(T, P)s]
        we assume the temps and pressures give all positive, defined rates
    """
    # Get list of the sorted pressures, ignoring the high-pressure limit rates
    pressures = [pressure for pressure in tk_dct
                 if pressure != 'high']
    pressures.sort()

    # Set the low- and high-pressure if not specified by user
    if plow is None:
        plow = min(pressures)
    if phigh is None:
        phigh = max(pressures)

    # Check % difference for k(T, P) vals
    is_pressure_dependent = False
    if plow in tk_dct and phigh in tk_dct:

        # Loop over temps to examine for large % dif in k(T) at low- and high-P
        for temp_compare in assess_pdep_temps:
            # For low- and high-P, find the idx for the temp in temp_compare
            temps_low = tk_dct[plow][0]
            temps_high = tk_dct[phigh][0]
            temp_low_match = np.where(np.isclose(temps_low, temp_compare))[0]
            temp_high_match = np.where(np.isclose(temps_high, temp_compare))[0]
            if temp_low_match.size > 0 and temp_high_match.size > 0:
                temp_low_idx = temp_low_match[0]
                temp_high_idx = temp_high_match[0]
                # Grab the k(T, P) vale for the approprite temp and pressure
                ktp_low = tk_dct[plow][1][temp_low_idx]
                ktp_high = tk_dct[phigh][1][temp_high_idx]
                # Calculate the % difference and see if above threshold
                ktp_dif = (abs(ktp_low - ktp_high) / ktp_low) * 100.0
                if ktp_dif > tolerance:
                    is_pressure_dependent = True

    return is_pressure_dependent
