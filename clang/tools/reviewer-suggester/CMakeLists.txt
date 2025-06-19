find_package(pybind11 REQUIRED)
find_package(Python3 REQUIRED COMPONENTS Interpreter Development)

add_executable(suggest_reviewers
  main.cpp
  bind.cpp
)

target_link_libraries(suggest_reviewers
  PRIVATE
  clangBasic
  clangTooling
  pybind11::embed
  Python3::Python
)
