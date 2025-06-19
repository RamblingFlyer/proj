// bind.h
#ifndef BIND_H
#define BIND_H

#include <vector>
#include <string>
#include <utility>

std::vector<std::pair<std::string, double>> get_reviewer_suggestions(int pr_number);

#endif
