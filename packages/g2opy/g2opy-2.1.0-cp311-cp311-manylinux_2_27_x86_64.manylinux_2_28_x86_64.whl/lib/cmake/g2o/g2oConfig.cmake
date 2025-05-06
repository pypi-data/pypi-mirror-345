include(CMakeFindDependencyMacro)

if (0)
  find_dependency(OpenGL)
endif()
find_dependency(Eigen3)

if (0)
  find_dependency(OpenGL)
endif()

# Find spdlog if g2o was build with support for it
if (0)
  find_dependency(spdlog)
endif()

include("${CMAKE_CURRENT_LIST_DIR}/g2oTargets.cmake")
