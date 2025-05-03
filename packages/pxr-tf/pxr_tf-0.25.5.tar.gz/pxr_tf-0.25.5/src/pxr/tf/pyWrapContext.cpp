// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "./pyWrapContext.h"
#include "./diagnosticLite.h"
#include "./instantiateSingleton.h"

namespace pxr {

TF_INSTANTIATE_SINGLETON(Tf_PyWrapContextManager);

Tf_PyWrapContextManager::Tf_PyWrapContextManager()
{
    // initialize the stack of context names
    _contextStack.clear();
}

}  // namespace pxr
