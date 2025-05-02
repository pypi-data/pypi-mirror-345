// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "./errorTransport.h"

namespace pxr {

void
TfErrorTransport::_PostImpl()
{
    TfDiagnosticMgr::GetInstance()._SpliceErrors(_errorList);
}

}  // namespace pxr
