import os
import ctypes
import numpy as np
import pandas as pd
import pyDOE as pydoe
from st7py import *
from St7API import *
from settings import *


def get_beam_material_property(uid,propnum):
    """
    gets beam material property data as array of doubles
    """
    data = (ctypes.c_double*9)()
    chkErr(St7GetBeamMaterialData(uid,propnum,data))
    return data


def set_beam_material_property(uid, propnums, value, propname='ipBeamModulus', disp=False):
    """
    sets a single modulus to single or multiple st7 property numbers.
    defaults to setting beam elastic modulus, ipBeamModulus
    """
    for prop in propnums:
        Double = ctypes.c_double*9
        Doubles = Double()
        chkErr(St7GetBeamMaterialData(uid,prop,Doubles))
        Doubles[propname] = value
        chkErr(St7SetBeamMaterialData(uid,prop,Doubles))
    [print('Beam Propnum: {}\tAssigned {} as {}'.format(x,propname,value)) for x in propnums if disp==True]


def set_plate_iso_material_property(uid, props, value, propname='ipPlateIsoModulus',disp=False):
    """
    sets desired material data to isotropic plates.
    defaults to ipPlateIsoModulus assignment
    """
    for prop in props:
        Double = ctypes.c_double*8
        Doubles = Double()
        chkErr(St7GetPlateIsotropicMaterial(uid,prop,Doubles))
        Doubles[propname] = value
        chkErr(St7SetPlateIsotropicMaterial(uid,prop,Doubles))
    [print('Plate Propnum: {}\tAssigned {} as {}'.format(x, propname, value)) for x in propnums if disp==True]


def set_plate_ortho_material_property_e(uid, propnums, value, disp=False):
    """
    sets a value[0] and value[1] to ortho plate modulus 1 and 2 respectively for
    each prop in propnums
    """
    for prop in propnums:
        Double = ctypes.c_double*18
        Doubles = Double()
        chkErr(St7GetPlateOrthotropicMaterial(uid,prop,Doubles))
        Doubles[ipPlateOrthoModulus1] = value[0]
        Doubles[ipPlateOrthoModulus2] = value[1]
        chkErr(St7SetPlateOrthotropicMaterial(uid,prop,Doubles))


def get_node_stiffness(uid=1,node=1,fcase=1):
    trans = (ctypes.c_double*3)()
    rot = (ctypes.c_double*3)()
    ucs = ctypes.c_long(1)
    # don't wrap in chkErr - throws error code 10 if no restraint originally assigned (so stupid)
    St7GetNodeKTranslation3F(uid, node, fcase, ucs, trans)
    St7GetNodeKRotation3F(uid, node, fcase, ucs, rot)
    return np.hstack((trans, rot))


def set_node_stiffness(uid=1,node=1,fcase=1,value=[0,0,0,0,0,0],disp=False):
    # get original node stiffness (for correct data type). do this directly instead of calling get_node_stiffness function bc it returns as np.hstacked
    kt = (ctypes.c_double*3)()
    kr = (ctypes.c_double*3)()
    ucs = ctypes.c_long(1)
    St7GetNodeKTranslation3F(uid, node, fcase, ucs, kt)
    St7GetNodeKRotation3F(uid, node, fcase, ucs, kr)
    if disp: print('Model-ID {} : Node {} : Original Stiffness {}'.format(uid,node,np.hstack((kt,kr))))
    k = get_node_stiffness(uid,node,fcase)
    kt[:] = value[:3]
    kr[:] = value[3:]
    chkErr(St7SetNodeKTranslation3F(uid, node, fcase, ucs, kt))
    chkErr(St7SetNodeKRotation3F(uid, node, fcase, ucs, kr))
    if disp: print('Model-ID {} : Node {} : Updated Stiffness {}'.format(uid,node,np.hstack((kt,kr))))


def get_node_restraint(uid=1,node=1,fcase=1):
    restraint = (ctypes.c_long*6)()
    displacement = (ctypes.c_double*6)()
    # don't use chkErr wrapper to avoid throwing 'missing data' error 10
    St7GetNodeRestraint6(uid,node, fcase, ctypes.c_long(1), restraint, displacement)
    return restraint


def set_node_restraint(uid=1,node=1,fcase=1, value=[1,1,1,0,0,0]):
    # get current restraint and displacement on node for proper c data type
    restraint = get_node_restraint(uid,node,fcase)
    displacement = get_node_initial_displacement(uid, node, fcase)
    # replace values w/ those given
    restraint[:] = value
    chkErr(St7SetNodeRestraint6(uid, node, fcase, ctypes.c_long(1), restraint, displacement))


def get_node_initial_displacement(uid=1,node=1,fcase=1):
    restraint = (ctypes.c_long*6)()
    displacement = (ctypes.c_double*6)()
    # don't use chkErr wrapper to avoid throwing 'missing data' error 10
    St7GetNodeRestraint6(uid,node, fcase, ctypes.c_long(1), restraint, displacement)
    return displacement


def set_node_initial_displacement(uid=1,node=1,fcase=1, value=[1,1,1,0,0,0]):
    # get current restraint and displacement on node for proper c data type
    restraint = get_node_restraint(uid,node,fcase)
    displacement = get_node_initial_displacement(uid, node, fcase)
    # replace values w/ those given
    displacement[:] = value
    chkErr(St7SetNodeRestraint6(uid, node, fcase, ctypes.c_long(1), restraint, displacement))


def gen_result_name(base_name, uid,result_ext,log_ext):
    """
    adds *_<uid>* to model file name for nfa results and log files
    """
    result_file = os.path.splitext(base_name)[0] + '_{}'.format(uid) + result_ext.upper()
    log_file = os.path.splitext(base_name)[0] + '_{}'.format(uid) + log_ext.upper()
    return result_file, log_file


def gen_start_values(n=1,fname = 'cal_start_values.csv'):
    """
    generates n latin hypercube experiments and saves them to disk.
    this creates a dependency on pyDOE library (bsd license)
    """
    values = pydoe.lhs(n)
    np.savetxt(fname,values)


def load_from_xls(fname):
    return pd.read_excel(fname, sheet_name=None)


def set_barrier_modulus():
    pass


def set_deck_modulus():
    pass


def set_deck_density():
    pass


def set_deck_thickness():
    pass


def set_deck_height():
    pass


def set_kx_ends():
    a = np.array([get_node_stiffness(1,node,1) for node in np.arange(1,11)])
    

def set_kr_mid():
    pass


def set_steel_modulus():
    pass


def set_diaphragm_modulus():
    pass



def assign_parameters():
    pass


def run_nfa(uid):
    # load St7API
    start()

    # open st7 model from st7py Model class instance
    model = Model(filename = ST7_FILE, scratch = ST7_SCRATCH, uid = uid)
    model.open()

    # get total number of elements
    tots = model.totals()

    # run NFA solver using model filename and uid to name files
    nfa_file, nfa_log = gen_result_name(model.filename, uid,'.NFA','.NFL')
    nfa = NFA(uid = uid,
              filename = nfa_file,
              logname = nfa_log,
              fcase = NFA_FCASE,
              nsm = NFA_NSM,
              nmodes = NFA_NMODES)

    # run  nfa solver
    nfa.run(disp=True)

    freqs = nfa.getFrequencies()
    shapes = nfa.getModeShapes(nodes=np.arange(1,1334))


    # close model file and unload St7API
    model.close()
    stop()

    return freqs, shapes


def calibrate():
    pass





def main(uid):


    # load xls file w/ processing logic
    paras = pd.read_excel(XLS_FILE, sheet_name='parameters')
