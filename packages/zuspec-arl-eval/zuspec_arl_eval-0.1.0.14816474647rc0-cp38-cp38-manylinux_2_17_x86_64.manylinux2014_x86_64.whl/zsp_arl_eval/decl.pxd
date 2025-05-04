#****************************************************************************
#* arl_dm_eval decl.pxd
#*
#****************************************************************************
cimport vsc_dm.decl as vsc
cimport vsc_solvers.decl as vsc_solvers
cimport zsp_arl_dm.decl as arl_dm
cimport debug_mgr.decl as dm
cimport pyapi_compat_if.decl as pyapi

from libcpp.string cimport string as cpp_string
from libcpp.vector cimport vector as cpp_vector
from libcpp.memory cimport unique_ptr
from libcpp cimport bool
from libc.stdint cimport int32_t, int64_t, uint64_t
cimport cpython.ref as cpy_ref

ctypedef EvalThreadData *EvalThreadDataP
ctypedef IFactory *IFactoryP
ctypedef IEvalContext *IEvalContextP
ctypedef IEvalThread *IEvalThreadP
ctypedef IEvalThreadId *IEvalThreadIdP

cdef extern from "zsp/arl/eval/IFactory.h" namespace "zsp::arl::eval":
    cdef cppclass IFactory:
        void init(dm.IDebugMgr *)

        IModelEvaluator *mkModelEvaluator(
            ModelEvaluatorKind      kind,
            vsc_solvers.IFactory    *solvers_f,
            arl_dm.IContext         *ctxt)

        IEvalContext *mkEvalContextFullElab(
            vsc_solvers.IFactory            *solvers_f,
            arl_dm.IContext                 *ctxt,
            const vsc_solvers.IRandState    *randstate,
            pyapi.IPyEval                   *pyeval,
            arl_dm.IDataTypeComponent       *root_comp,
            arl_dm.IDataTypeAction          *root_action,
            IEvalBackend                    *backend)

# cdef extern from "zsp/arl/eval/IEvalResult.h" namespace "zsp::arl::eval":
#     cdef enum EvalResultKind:
#         ResultKind_Void "zsp::arl::eval::EvalResultKind::Void"
#         ResultKind_Val "zsp::arl::eval::EvalResultKind::Val"
#         ResultKind_Ref "zsp::arl::eval::EvalResultKind::Ref"
#         ResultKind_Break "zsp::arl::eval::EvalResultKind::Break"
#         ResultKind_Continue "zsp::arl::eval::EvalResultKind::Continue"

#     cdef cppclass IEvalResult(vsc.IModelVal):
#         pass

cdef extern from "zsp/arl/eval/IEval.h" namespace "zsp::arl::eval":
    cdef enum EvalFlags "zsp::arl::eval::EvalFlags":
        EvalFlags_NoFlags "zsp::arl::eval::EvalFlags::NoFlags"
        EvalFlags_Complete "zsp::arl::eval::EvalFlags::Complete"
        EvalFlags_Error "zsp::arl::eval::EvalFlags::Error"
        EvalFlags_Break "zsp::arl::eval::EvalFlags::Break"
        EvalFlags_Continue "zsp::arl::eval::EvalFlags::Continue"
        EvalFlags_Return "zsp::arl::eval::EvalFlags::Return"

    cdef cppclass IEval:
        bool eval()
        bool hasFlags(EvalFlags flags) const
        vsc.ValRef getResult()
        void setResult(const vsc.ValRef &, EvalFlags flags)


cdef extern from "zsp/arl/eval/IEvalBackend.h" namespace "zsp::arl::eval":
    cdef cppclass IEvalBackend:
        void enterThreads(const cpp_vector[IEvalThreadP] &)

        void enterThread(IEvalThread *)

        void leaveThread(IEvalThread *)

        void leaveThreads(const cpp_vector[IEvalThreadP] &)

        void callFuncReq(
            IEvalThread                     *thread,
            arl_dm.IDataTypeFunction        *func_t,
            const cpp_vector[vsc.ValRef]    &params)

        void emitMessage(const cpp_string &msg)

cdef extern from "zsp/arl/eval/IEvalContext.h" namespace "zsp::arl::eval":
    cdef cppclass IEvalContext(IEval):
        IEvalBackend *getBackend() const
        void setBackend(IEvalBackend *b)
        const cpp_vector[arl_dm.IDataTypeFunctionP] &getSolveFunctions() const
        const cpp_vector[arl_dm.IDataTypeFunctionP] &getTargetFunctions() const
        bool addPyModule(const cpp_string &, pyapi.PyEvalObj *mod)

        vsc.ValRefInt mkValRefInt(int64_t value, bool is_signed, int32_t width)
        vsc.ValRefInt getAddrHandleValue(const vsc.ValRef &)
        # IEvalResult *mkEvalResultVal(vsc.IModelVal *val)
        # IEvalResult *mkEvalResultValS(int64_t val, int32_t bits)
        # IEvalResult *mkEvalResultValU(uint64_t val, int32_t bits)
        # IEvalResult *mkEvalResultKind(EvalResultKind kind)
        # IEvalResult *mkEvalResultRef(vsc.IModelField *ref)

#        const cpp_vector[arl_dm.IModelFieldExecutor] &getFunctions() const

cdef extern from "EvalBackendClosure.h" namespace "zsp::arl::eval":
    cdef cppclass EvalBackendClosure(IEvalBackend):
        EvalBackendClosure(cpy_ref.PyObject *)

cdef extern from "zsp/arl/eval/IEvalThreadId.h" namespace "zsp::arl::eval":
    cdef cppclass IEvalThreadId:
        pass

cdef extern from "zsp/arl/eval/IEvalThread.h" namespace "zsp::arl::eval":
    cdef cppclass IEvalThread(IEval):
        void setThreadId(IEvalThreadId *)
        IEvalThreadId *getThreadId()
        vsc.ValRefInt mkValRefInt(int64_t value, bool is_signed, int32_t width)
        vsc.ValRefInt getAddrHandleValue(const vsc.ValRef &)
        # IEvalResult *mkEvalResultVal(vsc.IModelVal *val)
        # IEvalResult *mkEvalResultValS(int64_t val, int32_t bits)
        # IEvalResult *mkEvalResultValU(uint64_t val, int32_t bits)
        # IEvalResult *mkEvalResultKind(EvalResultKind kind)
        # IEvalResult *mkEvalResultRef(vsc.IModelField *ref)

cdef extern from "EvalThreadData.h" namespace "zsp::arl::eval":
    cdef cppclass EvalThreadData(IEvalThreadId):
        EvalThreadData(cpy_ref.PyObject *)
        object getData() const

cdef extern from "zsp/arl/eval/IModelEvaluator.h" namespace "zsp::arl::eval":
    cdef enum ModelEvaluatorKind "zsp::arl::eval::ModelEvaluatorKind" :
        ModelEvaluatorKind_FullElab "zsp::arl::eval::ModelEvaluatorKind::FullElab"
        ModelEvaluatorKind_IncrElab "zsp::arl::eval::ModelEvaluatorKind::IncrElab"

    cdef cppclass IModelEvaluator:
        arl_dm.IModelEvalIterator *eval(
            const vsc_solvers.IRandState    *randstate,
            arl_dm.IModelFieldComponent     *root_comp,
            arl_dm.IDataTypeAction          *root_action)


