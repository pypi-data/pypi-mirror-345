// Copyright 2024 Pixar
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Copyright Eric Niebler 2005.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)
//
// Credits:
//   Andreas Kl\:ockner for fixing increment() to handle
//   error conditions.
//
// Modified by Jeremy Retailleau.

#include "../object.hpp"
#include "../handle.hpp"
#include "./stl_iterator_core.hpp"

namespace pxr { namespace boost { namespace python { namespace objects
{ 

stl_input_iterator_impl::stl_input_iterator_impl()
  : it_()
  , ob_()
{
}

stl_input_iterator_impl::stl_input_iterator_impl(pxr::boost::python::object const &ob)
  : it_(ob.attr("__iter__")())
  , ob_()
{
    this->increment();
}

void stl_input_iterator_impl::increment()
{
    this->ob_ = pxr::boost::python::handle<>(
        pxr::boost::python::allow_null(PyIter_Next(this->it_.ptr())));
    if (PyErr_Occurred())
        throw pxr::boost::python::error_already_set();
}

bool stl_input_iterator_impl::equal(stl_input_iterator_impl const &that) const
{
    return !this->ob_ == !that.ob_;
}

pxr::boost::python::handle<> const &stl_input_iterator_impl::current() const
{
    return this->ob_;
}

}}}} // namespace pxr::boost::python::objects
