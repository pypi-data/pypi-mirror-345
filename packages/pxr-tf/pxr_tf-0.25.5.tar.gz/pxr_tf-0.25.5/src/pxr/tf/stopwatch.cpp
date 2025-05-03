// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "./stopwatch.h"

#include <ostream>


namespace pxr {


std::ostream &
operator<<(std::ostream& out, const TfStopwatch& s)
{
    return out << s.GetSeconds() << " seconds";
}

}  // namespace pxr
