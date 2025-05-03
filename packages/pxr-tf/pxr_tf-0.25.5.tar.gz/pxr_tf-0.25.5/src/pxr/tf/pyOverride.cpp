// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "./pyOverride.h"

namespace pxr {

TfPyMethodResult::TfPyMethodResult(TfPyMethodResult const &other)
{
    TfPyLock lock;
    m_obj = other.m_obj;
}

TfPyMethodResult::~TfPyMethodResult()
{
    TfPyLock lock;
    m_obj.reset();
}

TfPyMethodResult &
TfPyMethodResult::operator=(TfPyMethodResult const &other)
{
    if (this != &other) {
        TfPyLock lock;
        m_obj = other.m_obj;
    }
    return *this;
}

}  // namespace pxr
