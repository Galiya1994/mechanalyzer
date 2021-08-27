""" ThermFit Interface to CBH code used to generate and update
    the mechanism oriented objects with species required to
    form the complete basis of heats-of-formation for species
    currently comprising some mechanism and stored in the
    the species dictionary.
"""

import os
import automol.inchi
import automol.geom
from phydat import phycon
import autorun
from mechanalyzer.inf import rxn as rinfo
import thermfit.cbh


# Set up the references for building
def prepare_basis(ref_scheme, spc_dct, spc_names,
                  zrxn=None, print_log=True, nprocs=1):
    """ Main callable function to generate the reference
        basis molecules used in heat-of-formation calculations

        Executed in parallel using Python MultiProcessing
        module if nprocs set above 1. Parallelization occurs
        over the species list.

        species basis_dct[name] = ()
        ts basis_dct[name] = ()
    """

    args = (ref_scheme, spc_dct, zrxn, print_log)
    basis_dcts = autorun.execute_function_in_parallel(
        _prepare_basis, spc_names, args, nprocs=nprocs)

    basis_dct = {}
    for dct in basis_dcts:
        basis_dct.update(dct)

    return basis_dct


def _prepare_basis(ref_scheme, spc_dct, zrxn, print_log,
                   spc_names, output_queue=None):
    """ Prepare references
    """

    # Get objects from spc_names
    spc_str = ', '.join(spc_names)
    spc_ichs = [spc_dct[spc]['inchi'] for spc in spc_names]

    # Begin prints
    if print_log:
        print('Process {} prepping species: {}'.format(os.getpid(), spc_str))

    # Print the message
    msg = '\nDetermining reference molecules for scheme: {}'.format(ref_scheme)
    msg += '\n'

    basis_dct = {}
    for spc_name, spc_ich in zip(spc_names, spc_ichs):

        msg += '\nDetermining basis for species: {}'.format(spc_name)

        # Build the basis set and coefficients for spc/TS
        if zrxn is not None:
            rcls = automol.reac.reaction_class(zrxn)
            radrad = automol.reac.is_radical_radical(zrxn)
            if (rcls, radrad) in thermfit.cbh.CBH_TS_CLASSES:
                scheme = ref_scheme
                if '_' in scheme:
                    scheme = 'cbh' + scheme.split('_')[1]
            else:
                scheme = 'basic'
            spc_basis, coeff_basis = thermfit.cbh.ts_basis(
                zrxn, scheme)
        else:
            spc_basis, coeff_basis = thermfit.cbh.species_basis(
                spc_ich, ref_scheme)

        # Add stereochemistry to the basis
        # basis either single InChI, or ((InChI,), (InChI,))
        ste_basis = ()
        for bas in spc_basis:
            if isinstance(bas, str):
                ste_basis += (automol.inchi.add_stereo(bas),)
            else:
                ste_basis += (
                    (tuple(automol.inchi.add_stereo(b) for b in bas[0]),
                     tuple(automol.inchi.add_stereo(b) for b in bas[1])),
                )

        # need to figure out print for TS basis
        # msg += '\nInChIs for basis set: {}'.format('\n  '.join(ste_basis))

        # Add to the dct containing info on the species basis
        basis_dct[spc_name] = (ste_basis, coeff_basis)

    # Print log message if it is desired
    if print_log:
        print(msg)

    # Add results to multiprocessing.Queue obj passed in
    output_queue.put((basis_dct,))


# Build a dictionary of unique basis references that need to be added
def unique_basis_species(basis_dct, spc_dct):
    """ Checks to see which species comprising the lists of
        heat-of-formation basis species (provided in the basis dct)
        currently exist in the mechanism species dictionary.

        If a basis molecule is found to be absent a sub-species
        dictionary is created and added to the spc dictionary.

        :param basis_dct: basis molecules for a set of species
        :type basis dct: dict[str: tuple(str)]
    """

    def _spc_ref_unique(ref, mech_ichs):
        """ Determine if InChI is unique
        """
        return ref not in mech_ichs

    def _ts_ref_unique(ref, mech_ichs):
        """ Determine if lst of inchis for ts is unique """
        return (
            _spc_ref_unique(ref, mech_ichs) or
            _spc_ref_unique(ref[::-1], mech_ichs)
        )

    # Generate list of all species currently in the spc dct
    mech_ichs = tuple(spc_dct[spc]['inchi'] for spc in spc_dct.keys()
                      if 'ts' not in spc)

    # Generate list of all prospective basis species
    unique_refs_dct = {}
    cnt = 1
    for name, (basis, _) in basis_dct.items():
        for bas in basis:
            # bas spc is (1) string = species, (2) ((str,), (str,))
            if isinstance(bas, str):
                if _spc_ref_unique(bas, mech_ichs):
                    ref_name = 'REF_{}'.format(cnt)
                    unique_refs_dct[ref_name] = create_spec(bas)
                    mech_ichs += (bas,)
                    cnt += 1
            else:
                if _ts_ref_unique(bas, mech_ichs):
                    ref_name = 'TS_REF_{}'.format(cnt)
                    unique_refs_dct[ref_name] = create_ts_spc(
                        bas, spc_dct, spc_dct[name]['mult'])
                    mech_ichs += (bas,)
                    cnt += 1

    return unique_refs_dct


# Create dictionries of information for species/TS
def create_ts_spc(ref, spc_dct, mult):
    """ add a ts species to the species dictionary
    """

    # Obtain the Reaction InChIs, Charges, Mults
    print('ref test', ref)
    reacs, prods = ref[0], ref[1]
    rxn_ichs = (
        tuple(automol.inchi.add_stereo(ich) for ich in reacs if ich),
        tuple(automol.inchi.add_stereo(ich) for ich in prods if ich)
    )

    rxn_muls, rxn_chgs = (), ()
    for rgts in (reacs, prods):
        rgt_muls, rgt_chgs = (), ()
        for rgt in rgts:
            found = False
            for dct in spc_dct.values():
                if 'inchi' in dct:
                    if dct['inchi'] == rgt:
                        rgt_muls += (dct['mult'],)
                        rgt_chgs += (dct['charge'],)
                        found = True
                        break
            if not found:
                new_spc = create_spec(rgt)
                rgt_muls += (new_spc['mult'],)
                rgt_chgs += (new_spc['charge'],)
        rxn_muls += (rgt_muls,)
        rxn_chgs += (rgt_chgs,)

    return {
        'reacs': list(reacs),
        'prods': list(prods),
        'charge': 0,
        'inchi': '',
        'mult': mult,
        'ts_locs': (0,),
        'rxn_info': rinfo.from_data(rxn_ichs, rxn_chgs, rxn_muls, mult)
    }


def create_spec(ich, charge=0,
                mc_nsamp=(True, 3, 1, 3, 100, 12),
                hind_inc=30.):
    """ add a species to the species dictionary
    """
    rad = automol.formula.electron_count(automol.inchi.formula(ich)) % 2
    mult = 1 if not rad else 2

    return {
        'smiles': automol.inchi.smiles(ich),
        'inchi': ich,
        'inchikey': automol.inchi.inchi_key(ich),
        'charge': charge,
        'mult': mult,
        'mc_nsamp': mc_nsamp,
        'hind_inc': hind_inc * phycon.DEG2RAD
    }