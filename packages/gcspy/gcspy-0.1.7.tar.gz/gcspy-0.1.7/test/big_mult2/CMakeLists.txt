add_executable(big_mult2 big_mult2.cc)
target_link_libraries(big_mult2 PUBLIC glasgow_constraint_solver)

find_package(Boost 1.74 COMPONENTS program_options REQUIRED)
include_directories(${Boost_INCLUDE_DIR})
target_link_libraries(big_mult2 LINK_PUBLIC ${Boost_LIBRARIES})