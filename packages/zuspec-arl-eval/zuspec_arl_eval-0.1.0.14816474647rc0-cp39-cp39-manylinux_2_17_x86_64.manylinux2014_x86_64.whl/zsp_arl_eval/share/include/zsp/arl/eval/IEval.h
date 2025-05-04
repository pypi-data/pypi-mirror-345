/**
 * IEval.h
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
#include "vsc/dm/IModelVal.h"
#include "vsc/dm/impl/ValRef.h"
#include "vsc/dm/impl/UP.h"
#include "zsp/arl/eval/IEvalValProvider.h"

namespace zsp {
namespace arl {
namespace eval {

enum class EvalFlags {
    NoFlags     = 0,
    AllFlags    = 0xFF,
    Complete    = (1 << 0),
    Error       = (1 << 1),
    Break       = (1 << 2),
    Continue    = (1 << 3),
    Return      = (1 << 4)
};

static inline EvalFlags operator | (const EvalFlags lhs, const EvalFlags rhs) {
        return static_cast<EvalFlags>(
                        static_cast<uint32_t>(lhs) | static_cast<uint32_t>(rhs));
}

static inline EvalFlags operator & (const EvalFlags lhs, const EvalFlags rhs) {
        return static_cast<EvalFlags>(
                        static_cast<uint32_t>(lhs) & static_cast<uint32_t>(rhs));
}

static inline EvalFlags operator ~ (const EvalFlags lhs) {
        return static_cast<EvalFlags>(~static_cast<uint32_t>(lhs));
}

class IEval;
using IEvalUP=vsc::dm::UP<IEval>;
class IEval :
    public virtual IEvalValProvider {
public:

    virtual ~IEval() { }

    /**
     * @brief Performs some work. 
     * 
     * @return true - if more work remains
     * @return false - if work is complete
     */
    virtual int32_t eval() = 0;

    virtual int32_t getIdx() = 0;

    virtual void setIdx(int32_t idx) = 0;

    virtual IEval *clone() = 0;

    virtual EvalFlags getFlags() const = 0;

    virtual bool hasFlags(EvalFlags flags) const = 0;

    virtual void setFlags(EvalFlags flags) = 0;

    virtual void clrFlags(EvalFlags flags=EvalFlags::AllFlags) = 0;

    virtual const vsc::dm::ValRef &getResult() const = 0;

    virtual void setResult(
        const vsc::dm::ValRef   &r,
        EvalFlags               flags=EvalFlags::Complete) = 0;

    virtual void setError(const char *fmt, ...) = 0;

#ifdef UNDEFINED
    /**
     * @brief Moves the result, clearing the result here
     * 
     * @return EvalResult& 
     */
    virtual vsc::dm::ValRef &moveResult() = 0;

    /**
     * @brief Sets the result, taking ownership of value data
     * 
     * @param r 
     */

    virtual void setVoidResult() = 0;

    virtual void setError(const std::string &msg) = 0;

    virtual bool haveError() const = 0;

    virtual const std::string &getError() const = 0;

    virtual void clrResult(bool clr_err=false) = 0;

    virtual bool haveResult() const = 0;
#endif

};

} /* namespace eval */
} /* namespace arl */
} /* namespace zsp */


