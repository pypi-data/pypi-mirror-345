// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_TF_SCOPE_DESCRIPTION_PRIVATE_H
#define PXR_TF_SCOPE_DESCRIPTION_PRIVATE_H

namespace pxr {

// Helper class for getting the TfScopeDescription stacks as human readable text
// for crash reporting.
class Tf_ScopeDescriptionStackReportLock
{
    Tf_ScopeDescriptionStackReportLock(
        Tf_ScopeDescriptionStackReportLock const &) = delete;
    Tf_ScopeDescriptionStackReportLock &operator=(
        Tf_ScopeDescriptionStackReportLock const &) = delete;
public:
    // Lock and compute the report message.
    Tf_ScopeDescriptionStackReportLock();

    // Unlock.
    ~Tf_ScopeDescriptionStackReportLock();

    // Get the report message.  This could be nullptr if it was impossible to
    // obtain the report.
    char const *GetMessage() const { return _msg; }
    
private:
    char const *_msg;
};

}  // namespace pxr

#endif // PXR_TF_SCOPE_DESCRIPTION_PRIVATE_H

