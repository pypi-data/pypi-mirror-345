/**
 * IBuiltinFuncInfo.h
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
#include <functional>
#include <vector>
#include "vsc/dm/impl/UP.h"
#include "vsc/dm/impl/ValRef.h"
#include "zsp/arl/eval/IEvalThread.h"

namespace zsp {
namespace arl {
namespace eval {

enum class BuiltinFuncFlags {
    NoFlags         = 0,
    RegFunc         = (1 << 0),
    RegFuncStruct   = (1 << 1),
    RegFuncWrite    = (1 << 2)
};

static inline BuiltinFuncFlags operator | (const BuiltinFuncFlags lhs, const BuiltinFuncFlags rhs) {
        return static_cast<BuiltinFuncFlags>(
                        static_cast<uint32_t>(lhs) | static_cast<uint32_t>(rhs));
}

static inline BuiltinFuncFlags operator & (const BuiltinFuncFlags lhs, const BuiltinFuncFlags rhs) {
        return static_cast<BuiltinFuncFlags>(
                        static_cast<uint32_t>(lhs) & static_cast<uint32_t>(rhs));
}

static inline BuiltinFuncFlags operator ~ (const BuiltinFuncFlags lhs) {
        return static_cast<BuiltinFuncFlags>(~static_cast<uint32_t>(lhs));
}

class IBuiltinFuncInfo;
using IBuiltinFuncInfoUP=vsc::dm::UP<IBuiltinFuncInfo>;
class IBuiltinFuncInfo {
public:

    using FuncT=std::function<void(
        IEvalThread *,
        dm::IDataTypeFunction *,
        const std::vector<vsc::dm::ValRef> &)>;

    virtual ~IBuiltinFuncInfo() { }

    virtual const FuncT &getImpl() const = 0;

    virtual BuiltinFuncFlags getFlags() const = 0;

    virtual bool hasFlags(BuiltinFuncFlags flags) const = 0;

};

} /* namespace eval */
} /* namespace arl */
} /* namespace zsp */


