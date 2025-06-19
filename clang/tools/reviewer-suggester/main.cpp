// main.cpp
#include <iostream>
#include <pybind11/embed.h>
#include "bind.h"  // Ensure this header is included

namespace py = pybind11;

int main(int argc, char** argv) {
    py::scoped_interpreter guard{};  // start Python interpreter

    if (argc != 2) {
        std::cerr << "Usage: suggest_reviewers <PR_number>\n";
        return 1;
    }

    int pr_number = std::stoi(argv[1]);

    try {
        auto reviewers = get_reviewer_suggestions(pr_number);
        std::cout << "Top Reviewers:\n";
        for (const auto& r : reviewers) {
            std::cout << r.first << " (score: " << r.second << ")\n";
        }
    } catch (const py::error_already_set& e) {
        std::cerr << "Python error: " << e.what() << "\n";
        return 2;
    }

    return 0;
}
