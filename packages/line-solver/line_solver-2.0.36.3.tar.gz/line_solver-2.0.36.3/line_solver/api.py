import jpype
import jpype.imports
import numpy as np
from jpype import JInt

from line_solver import jlineMatrixToArray, jlineMatrixFromArray

def cache_mva(gamma, m):
    ret = jpype.JPackage('jline').api.CACHE.cache_mva(jlineMatrixFromArray(gamma), jlineMatrixFromArray(m))
    pi = jlineMatrixFromArray(ret.pi)
    pi0 = jlineMatrixFromArray(ret.pi0)
    pij = jlineMatrixFromArray(ret.pij)
    x = jlineMatrixFromArray(ret.x)
    u = jlineMatrixFromArray(ret.u)
    E = jlineMatrixFromArray(ret.E)
    return pi, pi0, pij, x, u, E

def cache_prob_asy(gamma, m):
    return jpype.JPackage('jline').api.CACHE.cache_prob_asy(jlineMatrixFromArray(gamma), jlineMatrixFromArray(m))


def ctmc_uniformization(pi0, Q, t):
    return jlineMatrixToArray(
        jpype.JPackage('jline').api.CTMC.ctmc_uniformization(jlineMatrixFromArray(pi0), jlineMatrixFromArray(Q), t))


def ctmc_timereverse(matrix):
    return jlineMatrixToArray(jpype.JPackage('jline').api.CTMC.ctmc_timereverse(jlineMatrixFromArray(matrix)))


def ctmc_makeinfgen(matrix):
    return jlineMatrixToArray(jpype.JPackage('jline').api.CTMC.ctmc_makeinfgen(jlineMatrixFromArray(matrix)))


def ctmc_solve(matrix):
    return jlineMatrixToArray(jpype.JPackage('jline').api.CTMC.ctmc_solve(jlineMatrixFromArray(matrix)))


def dtmc_solve(matrix):
    return jlineMatrixToArray(jpype.JPackage('jline').api.DTMC.dtmc_solve(jlineMatrixFromArray(matrix)))


def dtmc_stochcomp(matrix, indexes):
    ind = jpype.java.util.ArrayList()
    for i in range(len(indexes)):
        ind.add(JInt(indexes[i]))
    return jlineMatrixToArray(jpype.JPackage('jline').api.DTMC.dtmc_stochcomp(jlineMatrixFromArray(matrix), ind))


def dtmc_timereverse(matrix):
    return jlineMatrixToArray(jpype.JPackage('jline').api.DTMC.dtmc_timereverse(jlineMatrixFromArray(matrix)))


def pfqn_ca(L, N, Z):
    pfqnNcReturn = jpype.JPackage('jline').api.PFQN.pfqn_ca(jlineMatrixFromArray(L), jlineMatrixFromArray(N),
                                                            jlineMatrixFromArray(Z))
    return pfqnNcReturn.G, pfqnNcReturn.lG

def pfqn_panacea(L, N, Z):
    pfqnNcReturn = jpype.JPackage('jline').api.PFQN.pfqn_panacea(jlineMatrixFromArray(L), jlineMatrixFromArray(N),
                                                            jlineMatrixFromArray(Z))
    return pfqnNcReturn.G, pfqnNcReturn.lG


def pfqn_bs(N, L, Z):
    pfqnAMVAReturn = jpype.JPackage('jline').api.PFQN.pfqn_bs(jlineMatrixFromArray(L), jlineMatrixFromArray(N),
                                                            jlineMatrixFromArray(Z))
    XN = jlineMatrixToArray(pfqnAMVAReturn.X)
    QN = jlineMatrixToArray(pfqnAMVAReturn.Q)
    UN = jlineMatrixToArray(pfqnAMVAReturn.U)
    RN = jlineMatrixToArray(pfqnAMVAReturn.R)
    TN = jlineMatrixToArray(pfqnAMVAReturn.R)
    AN = jlineMatrixToArray(pfqnAMVAReturn.R)

    XN = XN[0]
    CN = np.zeros_like(XN)

    for r in range(len(XN)):
        CN[r] = N[r] / XN[r]

    for i in range(len(QN)):
        for r in range(len(XN)):
            TN[i,r] = XN[r] # since visits are not known, we assume a cyclic topology
            AN[i,r] = XN[r] # since visits are not known, we assume a cyclic topology

    return XN, CN, QN, UN, RN, TN, AN

def pfqn_mva(N, L, Z):
    pfqnMVAReturn = jpype.JPackage('jline').api.PFQN.pfqn_mva(jlineMatrixFromArray(L), jlineMatrixFromArray(N),
                                                            jlineMatrixFromArray(Z))
    XN = jlineMatrixToArray(pfqnAMVAReturn.X)
    QN = jlineMatrixToArray(pfqnAMVAReturn.Q)
    UN = jlineMatrixToArray(pfqnAMVAReturn.U)
    RN = jlineMatrixToArray(pfqnAMVAReturn.R)
    TN = jlineMatrixToArray(pfqnAMVAReturn.R)
    AN = jlineMatrixToArray(pfqnAMVAReturn.R)

    XN = XN[0]
    CN = np.zeros_like(XN)

    for r in range(len(XN)):
        CN[r] = N[r] / XN[r]

    for i in range(len(QN)):
        for r in range(len(XN)):
            TN[i,r] = XN[r] # since visits are not known, we assume a cyclic topology
            AN[i,r] = XN[r] # since visits are not known, we assume a cyclic topology

    return XN, CN, QN, UN, RN, TN, AN

def pfqn_aql(N, L, Z):
    pfqnAMVAReturn = jpype.JPackage('jline').api.PFQN.pfqn_aql(jlineMatrixFromArray(L), jlineMatrixFromArray(N),
                                                              jlineMatrixFromArray(Z))
    XN = jlineMatrixToArray(pfqnAMVAReturn.X)
    QN = jlineMatrixToArray(pfqnAMVAReturn.Q)
    UN = jlineMatrixToArray(pfqnAMVAReturn.U)
    RN = jlineMatrixToArray(pfqnAMVAReturn.R)
    TN = jlineMatrixToArray(pfqnAMVAReturn.R)
    AN = jlineMatrixToArray(pfqnAMVAReturn.R)

    XN = XN[0]
    CN = np.zeros_like(XN)

    for r in range(len(XN)):
        CN[r] = N[r] / XN[r]

    for i in range(len(QN)):
        for r in range(len(XN)):
            TN[i,r] = XN[r] # since visits are not known, we assume a cyclic topology
            AN[i,r] = XN[r] # since visits are not known, we assume a cyclic topology

    return XN, CN, QN, UN, RN, TN, AN
