create_subdirectory_options(CLANG TOOL)

add_clang_subdirectory(apinotes-test)
add_clang_subdirectory(c-index-test)
add_clang_subdirectory(clang-diff)
add_clang_subdirectory(clang-format)
add_clang_subdirectory(clang-fuzzer)
add_clang_subdirectory(clang-import-test)
add_clang_subdirectory(clang-installapi)
add_clang_subdirectory(clang-linker-wrapper)
add_clang_subdirectory(clang-nvlink-wrapper)
add_clang_subdirectory(clang-offload-bundler)
add_clang_subdirectory(clang-offload-packager)
add_clang_subdirectory(clang-refactor)
add_clang_subdirectory(clang-scan-deps)
add_clang_subdirectory(clang-shlib)
add_clang_subdirectory(clang-sycl-linker)

if(CLANG_ENABLE_CIR)
  add_clang_subdirectory(cir-lsp-server)
  add_clang_subdirectory(cir-opt)
  add_clang_subdirectory(cir-translate)
endif()

if(CLANG_ENABLE_STATIC_ANALYZER)
  add_clang_subdirectory(clang-check)
  add_clang_subdirectory(clang-extdef-mapping)
  add_clang_subdirectory(scan-build)
  add_clang_subdirectory(scan-build-py)
  add_clang_subdirectory(scan-view)
endif()

add_clang_subdirectory(diagtool)
add_clang_subdirectory(driver)

# ✅ ✅ ✅ YOUR CUSTOM TOOL ENTRY GOES HERE
add_clang_subdirectory(reviewer-suggester)

add_clang_subdirectory(libclang)
add_clang_subdirectory(offload-arch)

# clang-tools-extra (external tools)
add_llvm_external_project(clang-tools-extra extra)

if(HAVE_CLANG_REPL_SUPPORT)
  add_clang_subdirectory(clang-repl)
endif()
