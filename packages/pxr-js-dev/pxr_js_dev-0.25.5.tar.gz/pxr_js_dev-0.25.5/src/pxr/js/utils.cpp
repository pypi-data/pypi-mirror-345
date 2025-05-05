// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

///
/// \file js/utils.cpp

#include "./utils.h"
#include <pxr/tf/diagnostic.h>

namespace pxr {

JsOptionalValue
JsFindValue(
    const JsObject& object,
    const std::string& key,
    const JsOptionalValue& defaultValue)
{
    if (key.empty()) {
        TF_CODING_ERROR("Key is empty");
        return std::nullopt;
    }

    JsObject::const_iterator i = object.find(key);
    if (i != object.end())
        return i->second;

    return defaultValue;
}

}  // namespace pxr
