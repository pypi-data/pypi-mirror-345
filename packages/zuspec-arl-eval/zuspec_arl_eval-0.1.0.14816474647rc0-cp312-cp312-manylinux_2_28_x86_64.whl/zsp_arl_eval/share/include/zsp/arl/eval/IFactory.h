/**
 * IFactory.h
 *
 * Copyright 2022 Matthew Ballance and Contributors
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may 
 * not use this file except in compliance with the License.  
 * You may obtain a copy of the License at:
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software 
 * distributed under the License is distributed on an "AS IS" BASIS, 
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
 * See the License for the specific language governing permissions and 
 * limitations under the License.
 *
 * Created on:
 *     Author: 
 */
#pragma once
#include "dmgr/IDebugMgr.h"
#include "pyapi-compat-if/IPyEval.h"
#include "vsc/solvers/IFactory.h"
#include "zsp/arl/dm/IContext.h"
#include "zsp/arl/eval/IComponentTreeData.h"
#include "zsp/arl/eval/IModelEvaluator.h"
#include "zsp/arl/eval/IEvalBackend.h"
#include "zsp/arl/eval/IEvalContext.h"
#include "zsp/arl/eval/IEvalStackFrame.h"

namespace zsp {
namespace arl {
namespace eval {



class IFactory {
public:

    virtual ~IFactory() { }

    virtual void init(dmgr::IDebugMgr *dmgr) = 0;

    virtual IComponentTreeData *mkComponentTreeData(
        arl::dm::IDataTypeComponent     *root_t) = 0;

    virtual IModelEvaluator *mkModelEvaluator(
        ModelEvaluatorKind          kind,
        vsc::solvers::IFactory      *solvers_f,
        arl::dm::IContext           *ctxt) = 0;

    virtual IEvalContext *mkEvalContextFullElab(
        vsc::solvers::IFactory          *solvers_f,
        arl::dm::IContext               *ctxt,
        const vsc::solvers::IRandState  *randstate,
        pyapi::IPyEval                  *pyeval,
        dm::IDataTypeComponent          *root_comp,
        dm::IDataTypeAction             *root_action,
        IEvalBackend                    *backend) = 0;

    virtual IEvalThread *mkEvalThread(
        IEvalBackend                    *backend,
        IEvalThread                     *parent) = 0;

    virtual IEvalContext *mkEvalContextFunctionStatic(
        vsc::solvers::IFactory                      *solvers_f,
        arl::dm::IContext                           *ctxt,
        const vsc::solvers::IRandState              *randstate,
        IEvalBackend                                *backend,
        dm::IDataTypeFunction                       *func,
        const std::vector<vsc::dm::ITypeExpr *>     &params) = 0;

    virtual IEvalContext *mkEvalContextFunctionContext(
        vsc::solvers::IFactory                      *solvers_f,
        arl::dm::IContext                           *ctxt,
        const vsc::solvers::IRandState              *randstate,
        IEvalBackend                                *backend,
        dm::IDataTypeFunction                       *func,
        vsc::dm::IModelField                        *func_ctxt,
        const std::vector<vsc::dm::ITypeExpr *>     &params) = 0;


};

} /* namespace eval */
} /* namespace arl */
} /* namespace zsp */


