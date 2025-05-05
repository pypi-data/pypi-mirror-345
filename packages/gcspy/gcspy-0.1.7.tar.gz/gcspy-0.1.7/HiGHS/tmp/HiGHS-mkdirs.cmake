# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

file(MAKE_DIRECTORY
  "/Users/matthewmcilree/PhD_Code/glasgow-constraint-solver/HiGHS/src/HiGHS"
  "/Users/matthewmcilree/PhD_Code/glasgow-constraint-solver/HiGHS/src/HiGHS-build"
  "/Users/matthewmcilree/PhD_Code/glasgow-constraint-solver/HiGHS"
  "/Users/matthewmcilree/PhD_Code/glasgow-constraint-solver/HiGHS/tmp"
  "/Users/matthewmcilree/PhD_Code/glasgow-constraint-solver/HiGHS/src/HiGHS-stamp"
  "/Users/matthewmcilree/PhD_Code/glasgow-constraint-solver/HiGHS/src"
  "/Users/matthewmcilree/PhD_Code/glasgow-constraint-solver/HiGHS/src/HiGHS-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "/Users/matthewmcilree/PhD_Code/glasgow-constraint-solver/HiGHS/src/HiGHS-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "/Users/matthewmcilree/PhD_Code/glasgow-constraint-solver/HiGHS/src/HiGHS-stamp${cfgdir}") # cfgdir has leading slash
endif()
