// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#ifndef PXR_JS_TYPES_H
#define PXR_JS_TYPES_H

/// \file js/types.h

#include <map>
#include <string>
#include <vector>

namespace pxr {

class JsValue;
typedef std::map<std::string, JsValue> JsObject;
typedef std::vector<JsValue> JsArray;

}  // namespace pxr

#endif // PXR_JS_TYPES_H
