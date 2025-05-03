
#include <pybind11/pybind11.h>
#include "../src/MyPypiDemo.h"

namespace py = pybind11;

PYBIND11_MODULE(PyCUploader, m) {
    py::class_<MyPypiDemo>(m, "MyPypiDemo")
    .def(pybind11::init<>())
    .def("add", &MyPypiDemo::add,
         py::arg("a"),
         py::arg("b"));
}
