import os
import jpype
import jpype.imports
import numpy as np
import pandas as pd
from jpype import JArray

from . import jlineMatrixToArray, is_interactive, jlineMapMatrixToArray, jlineMatrixFromArray
from .constants import SolverType, VerboseLevel, GlobalConstants


class Solver:
    def __init__(self, options, args):
        self.solveropt = options
        if len(args) >= 1:
            ctr = 0
            for ctr in range(len(args)):
                match args[ctr]:
                    case 'cutoff':
                        self.solveropt.obj.cutoff(args[ctr + 1])
                    case 'method':
                        self.solveropt.obj.method(args[ctr + 1])
                    case 'exact':
                        self.solveropt.obj.method('exact')
                        ctr -= 1
                    case 'keep':
                        self.solveropt.obj.keep(args[ctr + 1])
                    case 'seed':
                        self.solveropt.obj.seed(args[ctr + 1])
                    case 'samples':
                        self.solveropt.obj.samples(args[ctr + 1])
                    case 'verbose':
                        if isinstance(args[ctr + 1], bool):
                            if args[ctr + 1]:
                                self.solveropt.obj.verbose(jpype.JPackage('jline').lang.constant.VerboseLevel.STD)
                            else:
                                self.solveropt.obj.verbose(jpype.JPackage('jline').lang.constant.VerboseLevel.SILENT)
                        else:
                            match (args[ctr + 1]):
                                case VerboseLevel.SILENT:
                                    self.solveropt.obj.verbose(
                                        jpype.JPackage('jline').lang.constant.VerboseLevel.SILENT)
                                case VerboseLevel.STD:
                                    self.solveropt.obj.verbose(jpype.JPackage('jline').lang.constant.VerboseLevel.STD)
                                case VerboseLevel.DEBUG:
                                    self.solveropt.obj.verbose(jpype.JPackage('jline').lang.constant.VerboseLevel.DEBUG)
                ctr += 2
    def getName(self):
        return self.obj.getName()


class EnsembleSolver(Solver):
    def __init__(self, options, args):
        super().__init__(options, args)
        pass

class NetworkSolver(Solver):
    def __init__(self, options, args):
        super().__init__(options, args)
        pass

    def getAvgNodeTable(self):
        table = self.obj.getAvgNodeTable()

        # convert to NumPy

        QLen = np.array(list(table.getQLen()))
        Util = np.array(list(table.getUtil()))
        RespT = np.array(list(table.getRespT()))
        ResidT = np.array(list(table.getResidT()))
        ArvR = np.array(list(table.getArvR()))
        Tput = np.array(list(table.getTput()))

        cols = ['QLen', 'Util', 'RespT', 'ResidT', 'ArvR', 'Tput']
        nodes = list(table.getNodeNames())
        nodenames = []
        for i in range(len(nodes)):
            nodenames.append(str(nodes[i]))
        jobclasses = list(table.getClassNames())

        classnames = []
        for i in range(len(jobclasses)):
            classnames.append(str(jobclasses[i]))
        AvgTable = pd.DataFrame(np.concatenate([[QLen, Util, RespT, ResidT, ArvR, Tput]]).T, columns=cols)
        tokeep = ~(AvgTable <= 0.0).all(axis=1)
        AvgTable.insert(0, "JobClass", classnames)
        AvgTable.insert(0, "Node", nodenames)
        AvgTable = AvgTable.loc[tokeep]  # eliminate zero rows
        if not (
                GlobalConstants.getVerbose() == VerboseLevel.SILENT) and not self.solveropt.obj.verbose == VerboseLevel.SILENT:  # and not is_interactive():
            print(AvgTable)

        return AvgTable

    def getAvgChainTable(self):
        table = self.obj.getAvgChainTable()
        # convert to NumPy

        QLen = np.array(list(table.getQLen()))
        Util = np.array(list(table.getUtil()))
        RespT = np.array(list(table.getRespT()))
        ResidT = np.array(list(table.getResidT()))
        ArvR = np.array(list(table.getArvR()))
        Tput = np.array(list(table.getTput()))

        cols = ['QLen', 'Util', 'RespT', 'ResidT', 'ArvR', 'Tput']
        stations = list(table.getStationNames())
        statnames = []
        for i in range(len(stations)):
            statnames.append(str(stations[i]))
        jobchains = list(table.getChainNames())
        chainnames = []
        for i in range(len(jobchains)):
            chainnames.append(str(jobchains[i]))
        AvgChainTable = pd.DataFrame(np.concatenate([[QLen, Util, RespT, ResidT, ArvR, Tput]]).T, columns=cols)
        tokeep = ~(AvgChainTable <= 0.0).all(axis=1)
        AvgChainTable.insert(0, "Chain", chainnames)
        AvgChainTable.insert(0, "Station", statnames)
        AvgChainTable = AvgChainTable.loc[tokeep]  # eliminate zero rows
        if not (
                GlobalConstants.getVerbose() == VerboseLevel.SILENT) and not self.solveropt.obj.verbose == VerboseLevel.SILENT:  # and not is_interactive():
            print(AvgChainTable)

        return AvgChainTable


    def getAvgNodeChainTable(self):
        table = self.obj.getAvgNodeChainTable()
        # convert to NumPy

        QLen = np.array(list(table.getQLen()))
        Util = np.array(list(table.getUtil()))
        RespT = np.array(list(table.getRespT()))
        ResidT = np.array(list(table.getResidT()))
        ArvR = np.array(list(table.getArvR()))
        Tput = np.array(list(table.getTput()))

        cols = ['QLen', 'Util', 'RespT', 'ResidT', 'ArvR', 'Tput']
        nodes = list(table.getNodeNames())
        nodenames = []
        for i in range(len(nodes)):
            nodenames.append(str(nodes[i]))
        jobchains = list(table.getChainNames())
        chainnames = []
        for i in range(len(jobchains)):
            chainnames.append(str(jobchains[i]))
        AvgChainTable = pd.DataFrame(np.concatenate([[QLen, Util, RespT, ResidT, ArvR, Tput]]).T, columns=cols)
        tokeep = ~(AvgChainTable <= 0.0).all(axis=1)
        AvgChainTable.insert(0, "Chain", chainnames)
        AvgChainTable.insert(0, "Node", nodenames)
        AvgChainTable = AvgChainTable.loc[tokeep]  # eliminate zero rows
        if not (
                GlobalConstants.getVerbose() == VerboseLevel.SILENT) and not self.solveropt.obj.verbose == VerboseLevel.SILENT:  # and not is_interactive():
            print(AvgChainTable)

        return AvgChainTable

    def getAvgTable(self):
        table = self.obj.getAvgTable()

        # convert to NumPy

        QLen = np.array(list(table.getQLen()))
        Util = np.array(list(table.getUtil()))
        RespT = np.array(list(table.getRespT()))
        ResidT = np.array(list(table.getResidT()))
        ArvR = np.array(list(table.getArvR()))
        Tput = np.array(list(table.getTput()))

        cols = ['QLen', 'Util', 'RespT', 'ResidT', 'ArvR', 'Tput']

        stations = list(table.getStationNames())
        statnames = []
        for i in range(len(stations)):
            statnames.append(str(stations[i]))
        jobclasses = list(table.getClassNames())
        classnames = []
        for i in range(len(jobclasses)):
            classnames.append(str(jobclasses[i]))
        AvgTable = pd.DataFrame(np.concatenate([[QLen, Util, RespT, ResidT, ArvR, Tput]]).T, columns=cols)
        tokeep = ~(AvgTable <= 0.0).all(axis=1)
        AvgTable.insert(0, "JobClass", classnames)
        AvgTable.insert(0, "Station", statnames)
        AvgTable = AvgTable.loc[tokeep]  # eliminate zero rows
        if not (
                GlobalConstants.getVerbose() == VerboseLevel.SILENT) and not self.solveropt.obj.verbose == VerboseLevel.SILENT:  # and not is_interactive():
            print(AvgTable)

        return AvgTable

    def getAvgSysTable(self):
        table = self.obj.getAvgSysTable()

        # convert to NumPy
        SysRespT = np.array(list(table.getSysRespT()))
        SysTput = np.array(list(table.getSysTput()))

        cols = ['SysRespT', 'SysTput']
        jobchains = list(table.getChainNames())
        chains = []
        for i in range(len(jobchains)):
            chains.append(str(jobchains[i]))
        jobinchains = list(table.getInChainNames())
        inchains = []
        for i in range(len(jobinchains)):
            inchains.append(str(jobinchains[i]))
        AvgSysTable = pd.DataFrame(np.concatenate([[SysRespT, SysTput]]).T, columns=cols)
        tokeep = ~(AvgSysTable <= 0.0).all(axis=1)
        AvgSysTable.insert(0, "JobClasses", inchains)
        AvgSysTable.insert(0, "Chain", chains)
        AvgSysTable = AvgSysTable.loc[tokeep]  # eliminate zero rows
        if not (
                GlobalConstants.getVerbose() == VerboseLevel.SILENT) and not self.solveropt.obj.verbose == VerboseLevel.SILENT:
            print(AvgSysTable)
        return AvgSysTable

    def getAvgTput(self):
        Tput = jlineMatrixToArray(self.obj.getAvgTput())
        if not (
                GlobalConstants.getVerbose() == VerboseLevel.SILENT) and not self.solveropt.obj.verbose == VerboseLevel.SILENT:
            print(Tput)
        return Tput

    def getAvgResidT(self):
        ResidT = jlineMatrixToArray(self.obj.getAvgResidT())
        if not (
                GlobalConstants.getVerbose() == VerboseLevel.SILENT) and not self.solveropt.obj.verbose == VerboseLevel.SILENT:
            print(ResidT)
        return ResidT

    def getAvgArvR(self):
        ArvR = jlineMatrixToArray(self.obj.getAvgArvR())
        if not (
                GlobalConstants.getVerbose() == VerboseLevel.SILENT) and not self.solveropt.obj.verbose == VerboseLevel.SILENT:
            print(ArvR)
        return ArvR

    def getAvgUtil(self):
        Util = jlineMatrixToArray(self.obj.getAvgUtil())
        if not (
                GlobalConstants.getVerbose() == VerboseLevel.SILENT) and not self.solveropt.obj.verbose == VerboseLevel.SILENT:
            print(Util)
        return Util

    def getAvgQLen(self):
        QLen = jlineMatrixToArray(self.obj.getAvgQLen())
        if not (
                GlobalConstants.getVerbose() == VerboseLevel.SILENT) and not self.solveropt.obj.verbose == VerboseLevel.SILENT:
            print(QLen)
        return QLen

    def getAvgRespT(self):
        RespT = jlineMatrixToArray(self.obj.getAvgRespT())
        if not (
                GlobalConstants.getVerbose() == VerboseLevel.SILENT) and not self.solveropt.obj.verbose == VerboseLevel.SILENT:
            print(RespT)
        return RespT

    def getAvgSysTput(self):
        SysTput = jlineMatrixToArray(self.obj.getAvgSysTput())
        if not (
                GlobalConstants.getVerbose() == VerboseLevel.SILENT) and not self.solveropt.obj.verbose == VerboseLevel.SILENT:
            print(SysTput)
        return SysTput

    def getAvgSysRespT(self):
        SysRespT = jlineMatrixToArray(self.obj.getAvgSysRespT())
        if not (
                GlobalConstants.getVerbose() == VerboseLevel.SILENT) and not self.solveropt.obj.verbose == VerboseLevel.SILENT:
            print(SysRespT)
        return SysRespT

    def getCdfRespT(self):
        try:
            table = self.obj.getCdfRespT()
            distribC = self.obj.fluidResult.distribC
            CdfRespT = []
            for i in range(distribC.length):
                for c in range(distribC[i].length):
                    F = jlineMatrixToArray(distribC[i][c])
                    CdfRespT.append(F)
            return np.asarray(CdfRespT)
        except:
            return [[]]

class SolverCTMC(NetworkSolver):
    def __init__(self, *args):
        options = SolverOptions(jpype.JPackage('jline').lang.constant.SolverType.CTMC)
        super().__init__(options, args)
        model = args[0]
        self.obj = jpype.JPackage('jline').solvers.ctmc.SolverCTMC(model.obj, self.solveropt.obj)

    def getStateSpace(self):
        StateSpace = self.obj.getStateSpace()
        return jlineMatrixToArray(StateSpace.stateSpace), jlineMapMatrixToArray(StateSpace.localStateSpace.toMap())

    def getGenerator(self):
        generatorResult = self.obj.getGenerator()
        return jlineMatrixToArray(generatorResult.infGen), jlineMapMatrixToArray(generatorResult.eventFilt.toMap())#, jlineMapMatrixToArray(generatorResult.ev)

    @staticmethod
    def printInfGen(infGen, stateSpace):
        jpype.JPackage('jline').solvers.ctmc.SolverCTMC.printInfGen(jlineMatrixFromArray(infGen), jlineMatrixFromArray(stateSpace))

class SolverEnv(EnsembleSolver):
    def __init__(self, *args):
        options = SolverOptions(jpype.JPackage('jline').lang.constant.SolverType.ENV)
        super().__init__(options, [])
        model = args[0]
        solvers = jpype.JPackage('jline').solvers.NetworkSolver[len(args[1])]
        for i in range(len(solvers)):
            solvers[i] = args[1][i].obj
        self.obj = jpype.JPackage('jline').solvers.env.SolverEnv(model.obj, solvers, self.solveropt.obj)

    def getEnsembleAvg(self):
        return self.obj.getEnsembleAvg()

    def printAvgTable(self):
        self.obj.printAvgTable()


class SolverFluid(NetworkSolver):
    def __init__(self, *args):
        options = SolverOptions(jpype.JPackage('jline').lang.constant.SolverType.FLUID)
        super().__init__(options, args)
        model = args[0]
        self.obj = jpype.JPackage('jline').solvers.fluid.SolverFluid(model.obj, self.solveropt.obj)


class SolverJMT(NetworkSolver):
    def __init__(self, *args):
        options = SolverOptions(jpype.JPackage('jline').lang.constant.SolverType.JMT)
        super().__init__(options, args)
        model = args[0]
        self.jmtPath = jpype.JPackage('java').lang.String(os.path.dirname(os.path.abspath(__file__)) + "/JMT.jar")
        self.obj = jpype.JPackage('jline').solvers.jmt.SolverJMT(model.obj, self.solveropt.obj, self.jmtPath)

    def jsimwView(self):
        self.obj.jsimwView(self.jmtPath)

    def jsimgView(self):
        self.obj.jsimgView(self.jmtPath)


class SolverMAM(NetworkSolver):
    def __init__(self, *args):
        options = SolverOptions(jpype.JPackage('jline').lang.constant.SolverType.MAM)
        super().__init__(options, args)
        model = args[0]
        self.obj = jpype.JPackage('jline').solvers.mam.SolverMAM(model.obj, self.solveropt.obj)


class SolverMVA(NetworkSolver):
    def __init__(self, *args):
        options = SolverOptions(jpype.JPackage('jline').lang.constant.SolverType.MVA)
        super().__init__(options, args)
        model = args[0]
        self.obj = jpype.JPackage('jline').solvers.mva.SolverMVA(model.obj, self.solveropt.obj)


class SolverLQNS(Solver):
    def __init__(self, *args):
        options = SolverOptions(jpype.JPackage('jline').lang.constant.SolverType.LQNS)
        super().__init__(options, args)
        model = args[0]
        self.obj = jpype.JPackage('jline').solvers.lqns.SolverLQNS(model.obj, self.solveropt.obj)

    def getAvgTable(self):
        table = self.obj.getAvgTable()
        # convert to NumPy

        QLen = np.array(list(table.getQLen()))
        Util = np.array(list(table.getUtil()))
        RespT = np.array(list(table.getRespT()))
        ResidT = np.array(list(table.getResidT()))
        ArvR = np.array(list(table.getArvR()))
        Tput = np.array(list(table.getTput()))

        cols = ['QLen', 'Util', 'RespT', 'ResidT', 'ArvR', 'Tput']
        nodenames = list(table.getNodeNames())
        mynodenames = []
        for i in range(len(nodenames)):
            mynodenames.append(str(nodenames[i]))
        nodetypes = list(table.getNodeTypes())
        mynodetypes = []
        for i in range(len(nodetypes)):
            mynodetypes.append(str(nodetypes[i]))
        AvgTable = pd.DataFrame(np.concatenate([[QLen, Util, RespT, ResidT, ArvR, Tput]]).T, columns=cols)
        tokeep = ~(AvgTable <= 0.0).all(axis=1)
        AvgTable.insert(0, "NodeType", mynodetypes)
        AvgTable.insert(0, "Node", mynodenames)
        AvgTable = AvgTable.loc[tokeep]  # eliminate zero rows
        if not (
                GlobalConstants.getVerbose() == VerboseLevel.SILENT) and not self.solveropt.obj.verbose == VerboseLevel.SILENT:  # and not is_interactive():
            print(AvgTable)

        return AvgTable


class SolverLN(EnsembleSolver):
    def __init__(self, *args):
        options = SolverOptions(jpype.JPackage('jline').lang.constant.SolverType.LN)
        super().__init__(options, args)
        model = args[0]
        self.obj = jpype.JPackage('jline').solvers.ln.SolverLN(model.obj, self.solveropt.obj)


    def getAvgTable(self):
        table = self.obj.getAvgTable()
        # convert to NumPy

        QLen = np.array(list(table.getQLen()))
        Util = np.array(list(table.getUtil()))
        RespT = np.array(list(table.getRespT()))
        ResidT = np.array(list(table.getResidT()))
        ArvR = np.array(list(table.getArvR()))
        Tput = np.array(list(table.getTput()))

        cols = ['QLen', 'Util', 'RespT', 'ResidT', 'ArvR', 'Tput']
        nodenames = list(table.getNodeNames())
        mynodenames = []
        for i in range(len(nodenames)):
            mynodenames.append(str(nodenames[i]))
        nodetypes = list(table.getNodeTypes())
        mynodetypes = []
        for i in range(len(nodetypes)):
            mynodetypes.append(str(nodetypes[i]))
        AvgTable = pd.DataFrame(np.concatenate([[QLen, Util, RespT, ResidT, ArvR, Tput]]).T, columns=cols)
        tokeep = ~(AvgTable <= 0.0).all(axis=1)
        AvgTable.insert(0, "NodeType", mynodetypes)
        AvgTable.insert(0, "Node", mynodenames)
        AvgTable = AvgTable.loc[tokeep]  # eliminate zero rows
        if not (
                GlobalConstants.getVerbose() == VerboseLevel.SILENT) and not self.solveropt.obj.verbose == VerboseLevel.SILENT:  # and not is_interactive():
            print(AvgTable)

        return AvgTable

class SolverNC(NetworkSolver):
    def __init__(self, *args):
        options = SolverOptions(jpype.JPackage('jline').lang.constant.SolverType.NC)
        super().__init__(options, args)
        model = args[0]
        self.obj = jpype.JPackage('jline').solvers.nc.SolverNC(model.obj, self.solveropt.obj)


class SolverSSA(NetworkSolver):
    def __init__(self, *args):
        options = SolverOptions(jpype.JPackage('jline').lang.constant.SolverType.SSA)
        super().__init__(options, args)
        model = args[0]
        self.obj = jpype.JPackage('jline').solvers.ssa.SolverSSA(model.obj, self.solveropt.obj)

class SolverOptions():
    def __init__(self, solvertype):
        self.obj = jpype.JPackage('jline').solvers.SolverOptions(solvertype)

    def method(self, value):
        self.obj.method(value)

    def samples(self, value):
        self.obj.samples(value)

    def seed(self, value):
        self.obj.seed(value)

    def verbose(self, value):
        self.obj.verbose(value)


class CTMCOptions():
    def __init__(self):
        self.obj = jpype.JPackage('jline').solvers.CTMCOptions()


class EnvOptions():
    def __init__(self):
        self.obj = jpype.JPackage('jline').solvers.EnvOptions()


class FluidOptions():
    def __init__(self):
        self.obj = jpype.JPackage('jline').solvers.FluidOptions()


class JMTOptions():
    def __init__(self):
        self.obj = jpype.JPackage('jline').solvers.JMTOptions()


class LNOptions():
    def __init__(self):
        self.obj = jpype.JPackage('jline').solvers.LNOptions()


class LQNSOptions():
    def __init__(self):
        self.obj = jpype.JPackage('jline').solvers.LQNSOptions()


class MAMOptions():
    def __init__(self):
        self.obj = jpype.JPackage('jline').solvers.MAMOptions()


class MVAOptions():
    def __init__(self):
        self.obj = jpype.JPackage('jline').solvers.MVAOptions()


class NCOptions():
    def __init__(self):
        self.obj = jpype.JPackage('jline').solvers.NCOptions()


class SSAOptions():
    def __init__(self):
        self.obj = jpype.JPackage('jline').solvers.SSAOptions()
