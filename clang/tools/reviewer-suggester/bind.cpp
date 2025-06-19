// bind.cpp
#include <pybind11/embed.h>
#include <vector>
#include <string>
#include <utility>
#include "bind.h"

namespace py = pybind11;

std::vector<std::pair<std::string, double>> get_reviewer_suggestions(int pr_number) {
    // Set environment variables before initializing the interpreter
    setenv("PYTHONHOME", "/Users/aditya/Desktop/RVCE/SEM6/CD1/env", 1);
    setenv("PYTHONPATH", "/Users/aditya/Desktop/RVCE/SEM6/CD1/llvm-project copy 2/clang/tools/reviewer-suggester", 1);

    // Check if the interpreter is already initialized
    if (!Py_IsInitialized()) {
        py::initialize_interpreter();
    }

    py::module recommender = py::module::import("recommender");
    py::object result = recommender.attr("suggest_reviewers")(pr_number);

    std::vector<std::pair<std::string, double>> reviewers;  // Change float to double
    for (const auto& item : result) {
        auto tuple = item.cast<std::pair<std::string, double>>();  // Change float to double
        reviewers.push_back(tuple);
    }

    // Do not finalize the interpreter here to avoid issues with multiple calls
    return reviewers;
}
