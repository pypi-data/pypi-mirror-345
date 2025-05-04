#****************************************************************************
#* arl_dm_eval core.pxd
#*
#****************************************************************************
import ctypes
cimport debug_mgr.core as dm_core
cimport vsc_solvers.core as vsc_solvers
cimport zsp_arl_dm.core as arl_dm
from zsp_arl_eval cimport decl

from libc.stdint cimport int32_t
from libcpp cimport bool
from libcpp.string cimport string as cpp_string
cimport vsc_dm.core as vsc
cimport vsc_dm.decl as vsc_decl
cimport pyapi_compat_if.core as pyapi
cimport pyapi_compat_if.decl as pyapi_decl

cdef class Factory(object):
    cdef decl.IFactory      *_hndl
    cdef pyapi.PyEval       _pyeval

    cdef init(self, dm_core.Factory)

    cpdef EvalContext mkEvalContextFullElab(
        self,
        vsc_solvers.Factory           solvers_f,
        arl_dm.Context                ctxt,
        vsc_solvers.RandState         randstate,
        arl_dm.DataTypeComponent      root_comp,
        arl_dm.DataTypeAction         root_action,
        EvalBackend                   backend)

    cpdef ModelEvaluator mkModelEvaluator(
        self,
        kind,
        vsc_solvers.Factory solvers_f,
        arl_dm.Context      ctxt)

cdef class EvalBackend(object):
    cdef decl.EvalBackendClosure    *_hndl

cdef class Eval(object):
    cdef decl.IEval                 *_hndl
    cdef bool                       _owned

    cpdef bool eval(self)

    cpdef bool hasFlags(self, flags)

    cpdef vsc.ValRef getResult(self)

    cpdef void setResult(self, vsc.ValRef r, flags=*)

    @staticmethod
    cdef Eval mk(decl.IEval *hndl, bool owned=*)

cdef class EvalContext(object):
    cdef decl.IEvalContext          *_hndl
    cdef bool                       _owned

    cpdef bool eval(self)

    cpdef bool hasFlags(self, flags)

    cpdef vsc.ValRef getResult(self)

    cpdef getSolveFunctions(self)

    cpdef getTargetFunctions(self)

    cpdef bool addPyModule(self, str name, object mod)

    cpdef vsc.ValRefInt mkValRefInt(self, int value, bool is_signed, int width)

    cpdef vsc.ValRefInt getAddrHandleValue(self, vsc.ValRef val)

    # cpdef EvalResult mkEvalResultVal(self, vsc.ModelVal v)

    # cpdef EvalResult mkEvalResultValS(self, int val, int bits=*)

    # cpdef EvalResult mkEvalResultValU(self, int val, int bits=*)

    # cpdef EvalResult mkEvalResultKind(self, kind)

    # cpdef EvalResult mkEvalResultRef(self, vsc.ModelField ref)

    cdef decl.IEvalContext *asContext(self)

    @staticmethod
    cdef EvalContext mk(decl.IEvalContext *hndl, bool owned=*)

cdef class EvalThread(Eval):

    cpdef void setThreadId(self, obj)
    
    cpdef object getThreadId(self)

    cpdef vsc.ValRefInt mkValRefInt(self, int value, bool is_signed, int width)

    cpdef vsc.ValRefInt getAddrHandleValue(self, vsc.ValRef val)

    # cpdef EvalResult mkEvalResultVal(self, vsc.ModelVal v)

    # cpdef EvalResult mkEvalResultValS(self, int val, int bits=*)

    # cpdef EvalResult mkEvalResultValU(self, int val, int bits=*)

    # cpdef EvalResult mkEvalResultKind(self, kind)

    # cpdef EvalResult mkEvalResultRef(self, vsc.ModelField ref)

    cdef decl.IEvalThread *asThread(self)

    @staticmethod
    cdef EvalThread mk(decl.IEvalThread *hndl, bool owned=*)

cdef class ModelEvaluator(object):
    cdef decl.IModelEvaluator       *_hndl
    cdef bool                       _owned

    cpdef arl_dm.ModelEvalIterator eval(
        self,
        vsc_solvers.RandState           randstate,
        arl_dm.ModelFieldComponent      root_comp,
        arl_dm.DataTypeAction           root_action)

    @staticmethod
    cdef ModelEvaluator mk(decl.IModelEvaluator *hndl, bool owned=*)

    pass
    
    
