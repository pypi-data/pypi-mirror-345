/**
 * IEvalBackend.h
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
#include <vector>
#include "zsp/arl/eval/IEvalThread.h"
#include "zsp/arl/eval/IEvalThreadId.h"
#include "zsp/arl/dm/IDataTypeAction.h"
#include "zsp/arl/dm/IDataTypeFunction.h"
#include "zsp/arl/dm/IModelFieldAction.h"

namespace zsp {
namespace arl {
namespace eval {

class IEvalContext;
class IEvalBackend;
using IEvalBackendUP=vsc::dm::UP<IEvalBackend>;
class IEvalBackend {
public:

    virtual ~IEvalBackend() { }

    virtual void init(IEvalContext *ctxt) = 0;

    /**
     * @brief Start
     * 
     * @param threads 
     */
    virtual void enterThreads(
        const std::vector<IEvalThread *>    &threads) = 0;
    
    virtual void enterThread(IEvalThread *thread) = 0;

    virtual void leaveThread(IEvalThread *thread) = 0;

    virtual void leaveThreads(
        const std::vector<IEvalThread *>    &threads) = 0;

    virtual void enterAction(
        IEvalThread                         *thread,
        dm::IDataTypeAction                 *action_t,
        const vsc::dm::ValRef               &action_v) = 0;

    virtual void leaveAction(
        IEvalThread                         *thread,
        dm::IDataTypeAction                 *action_t,
        const vsc::dm::ValRef               &action_v) = 0;

    virtual void callFuncReq(
            IEvalThread                         *thread,
            dm::IDataTypeFunction               *func_t,
            const std::vector<vsc::dm::ValRef>  &params
    ) = 0;

    virtual void emitMessage(const std::string &msg) = 0;

};

} /* namespace eval */
} /* namespace arl */
} /* namespace zsp */


