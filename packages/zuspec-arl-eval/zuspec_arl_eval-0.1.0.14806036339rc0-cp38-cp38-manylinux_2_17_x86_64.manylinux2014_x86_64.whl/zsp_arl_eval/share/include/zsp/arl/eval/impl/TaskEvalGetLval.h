/**
 * TaskEvalGetLval.h
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
#include "dmgr/impl/DebugMacros.h"
#include "vsc/dm/impl/ValRefStruct.h"
#include "zsp/arl/dm/impl/VisitorBase.h"
#include "zsp/arl/eval/IEvalThread.h"

namespace zsp {
namespace arl {
namespace eval {



class TaskEvalGetLval : 
    public virtual dm::VisitorBase {
public:
    TaskEvalGetLval(
        dmgr::IDebugMgr     *dmgr,
        IEvalValProvider    *vp) : m_vp(vp), m_dbg(0) { 
        DEBUG_INIT("zsp::arl::eval::TaskEvalGetLval", dmgr);

    }

    virtual ~TaskEvalGetLval() { };

    vsc::dm::ValRef eval(vsc::dm::ITypeExpr *expr) {
        DEBUG_ENTER("eval");
        m_val.reset();
        expr->accept(m_this);
        DEBUG_LEAVE("eval %p", m_val);
        return m_val;
    }

	virtual void visitTypeExprArrIndex(vsc::dm::ITypeExprArrIndex *e) override {
        DEBUG_ENTER("visitTypeExprArrIndex");
        DEBUG("TODO: visitTypeExprArrIndex");
        DEBUG_LEAVE("visitTypeExprArrIndex");
    }

	virtual void visitTypeExprFieldRef(vsc::dm::ITypeExprFieldRef *e) override {
        int32_t path_idx = 0;
        DEBUG_ENTER("visitTypeExprFieldRef");

#ifdef UNDEFINED
        if (e->getPath().size() == 0) {
            DEBUG_ERROR("Path is empty");
            return;
        }

        DEBUG("root_ref_kind=%d offset=%d", 
            e->getRootRefKind(),
            e->getRootRefOffset());
        DEBUG("path.size=%d path_idx=%d index=%d",
            e->getPath().size(),
            path_idx,
            e->getPath().at(path_idx));
        DEBUG("vp=%p", m_vp);
        m_val = m_vp->getMutVal(
            e->getRootRefKind(),
            e->getRootRefOffset(),
            e->getPath().at(path_idx++)
        );
        // switch (e->getRootRefKind()) {
        //     case vsc::dm::ITypeExprFieldRef::RootRefKind::BottomUpScope: {
        //         IEvalStackFrame *frame = m_thread->stackFrame(e->getPath().at(path_idx++));
        //         var.setWeakRef(frame->getVariable(e->getPath().at(path_idx++)));
        //     } break;
        //     case vsc::dm::ITypeExprFieldRef::RootRefKind::TopDownScope: {
        //         vsc::dm::ValRefStruct scope_s(m_scope);
        //         var.setWeakRef(scope_s.getFieldRef(e->getPath().at(path_idx++)));
        //     } break;
        // }

        // vsc::dm::IModelField *field = 0;
        // if (path_idx >= e->getPath().size()) {
        //     m_val.setWeakRef(var);
        // } else {
        //     while (path_idx < e->getPath().size()) {
        //         vsc::dm::ValRefStruct val_s(var);
        //         var = val_s.getFieldRef(e->getPath().at(path_idx));
        //         DEBUG("Get field-ref @ %d", e->getPath().at(path_idx));
        //         path_idx++;
        //     }
        //     m_val.setWeakRef(var);
        // }

#endif /* UNDEFINED */

        DEBUG_LEAVE("visitTypeExprFieldRef");
    }

	virtual void visitTypeExprRefBottomUp(vsc::dm::ITypeExprRefBottomUp *e) override { 
        DEBUG_ENTER("visitTypeExprRefBottomUp");
        m_val = m_vp->getMutVal(
            vsc::dm::ITypeExprFieldRef::RootRefKind::BottomUpScope,
            e->getScopeOffset(),
            e->getSubFieldIndex());
        DEBUG_LEAVE("visitTypeExprRefBottomUp");
    }

	virtual void visitTypeExprRefTopDown(vsc::dm::ITypeExprRefTopDown *e) override { 
        DEBUG_ENTER("visitTypeExprRefTopDown");
        m_val = m_vp->getMutVal(
            vsc::dm::ITypeExprFieldRef::RootRefKind::TopDownScope,
            -1,
            -1);
        DEBUG_LEAVE("visitTypeExprRefTopDown");
    }

	virtual void visitTypeExprSubField(vsc::dm::ITypeExprSubField *e) override {
        DEBUG_ENTER("visitTypeExprSubField");
        e->getRootExpr()->accept(m_this);
        vsc::dm::ValRefStruct val_s(m_val);
        m_val = val_s.getFieldRef(e->getSubFieldIndex());
        DEBUG_LEAVE("visitTypeExprSubField");
    }

private:
    dmgr::IDebug            *m_dbg;
    IEvalValProvider        *m_vp;
    vsc::dm::ValRef         m_val;

};

}
}
}


