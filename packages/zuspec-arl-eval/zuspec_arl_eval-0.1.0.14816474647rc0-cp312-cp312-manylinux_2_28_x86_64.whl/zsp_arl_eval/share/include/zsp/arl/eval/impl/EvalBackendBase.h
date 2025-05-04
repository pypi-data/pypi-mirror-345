/**
 * EvalBackendBase.h
 *
 * Copyright 2023 Matthew Ballance and Contributors
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
#include "zsp/arl/eval/IEvalBackend.h"

namespace zsp {
namespace arl {
namespace eval {



class EvalBackendBase : public virtual IEvalBackend {
public:
    EvalBackendBase() { }

    virtual ~EvalBackendBase() { }

    virtual void init(IEvalContext *ctxt) override {
        m_ctxt = ctxt;
    }

    virtual void enterThreads(
        const std::vector<IEvalThread *>    &threads) override { }
    
    virtual void enterThread(IEvalThread *thread) override { }

    virtual void leaveThread(IEvalThread *thread) override { }

    virtual void leaveThreads(
        const std::vector<IEvalThread *>    &threads) override { }

    virtual void enterAction(
        IEvalThread                         *thread,
        dm::IDataTypeAction                 *action_t,
        const vsc::dm::ValRef               &action_v) override { }

    virtual void leaveAction(
        IEvalThread                         *thread,
        dm::IDataTypeAction                 *action_t,
        const vsc::dm::ValRef               &action_v) override { }

    virtual void callFuncReq(
            IEvalThread                         *thread,
            dm::IDataTypeFunction               *func_t,
            const std::vector<vsc::dm::ValRef>  &params) override { }

    virtual void emitMessage(const std::string &msg) override { }

protected:
    IEvalContext                        *m_ctxt;

};

}
}
}


