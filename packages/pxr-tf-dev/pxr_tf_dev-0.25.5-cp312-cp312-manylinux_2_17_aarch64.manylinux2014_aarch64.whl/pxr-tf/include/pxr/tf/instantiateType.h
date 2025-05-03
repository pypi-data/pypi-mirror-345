// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

/*
 * This header is not meant to be included in a .h file.
 * Complain if we see this header twice through.
 */

#ifdef PXR_TF_INSTANTIATE_TYPE_H
#error This file should only be included once in any given source (.cpp) file.
#endif

#define PXR_TF_INSTANTIATE_TYPE_H

#include <pxr/arch/attributes.h>
#include "./type.h"
#include "./refPtr.h"

namespace pxr {

template <typename T, bool AS_REF_PTR>
struct Tf_TypeFactoryType {
    struct FactoryType : public TfType::FactoryBase {
        TfRefPtr<T> New() { return T::New(); }
    };
};
template <class T>
struct TfTest_RefPtrFactory {
};

template <typename T>
struct Tf_TypeFactoryType<T, false> {
    struct FactoryType : public TfType::FactoryBase {
        T* New() { return new T; }
    };
};

// Make the type actually manufacturable.
template <typename T, bool MANUFACTURABLE>
struct Tf_MakeTypeManufacturable {
    static void Doit(TfType t) {
        typedef typename Tf_TypeFactoryType<T, TF_SUPPORTS_REFPTR(T)>::FactoryType FT;
        t.SetFactory<FT>();
    }
};

// Don't make it manufacturable.
template <typename T>
struct Tf_MakeTypeManufacturable<T, false> {
    static void Doit(TfType) {
    }
};
    
#define _TF_REMOVE_PARENS_HELPER(...) __VA_ARGS__
#define _TF_REMOVE_PARENS(parens) _TF_REMOVE_PARENS_HELPER parens

#define TF_NO_PARENT()            (pxr::TfType::Bases<>)
#define TF_1_PARENT(p1)            (pxr::TfType::Bases<p1 >)
#define TF_2_PARENT(p1,p2)  (pxr::TfType::Bases<p1, p2 >)
#define TF_INSTANTIATE_TYPE(Type, flags, Bases) \
    TF_REGISTRY_DEFINE_WITH_TYPE(pxr::TfType, Type) { \
        pxr::TfType t1 = pxr::TfType::Define<Type, _TF_REMOVE_PARENS(Bases) >(); \
        pxr::Tf_MakeTypeManufacturable<Type, (flags&pxr::TfType::MANUFACTURABLE)!=0 >::Doit(t1); \
    }

}  // namespace pxr
