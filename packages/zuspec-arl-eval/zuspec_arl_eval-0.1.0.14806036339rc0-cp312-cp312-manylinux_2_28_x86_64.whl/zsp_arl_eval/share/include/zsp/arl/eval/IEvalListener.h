/**
 * IEvalListener.h
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
#include "zsp/arl/dm/IModelFieldAction.h"

namespace zsp {
namespace arl {
namespace eval {



class IEvalListener {
public:

    virtual ~IEvalListener() { }

    virtual void enterThreads(const std::vector<IEvalThread *> &threads) = 0;

    virtual void enterThread(IEvalThread *t) = 0;

    virtual void enterAction(
        IEvalThread             *t,
        dm::IModelFieldAction   *action) = 0;

    virtual void leaveAction(
        IEvalThread             *t,
        dm::IModelFieldAction   *action) = 0;

    virtual void leaveThread(IEvalThread *t) = 0;

    virtual void leaveThreads(const std::vector<IEvalThread *> &threads) = 0;

};

} /* namespace eval */
} /* namespace arl */
} /* namespace zsp */


