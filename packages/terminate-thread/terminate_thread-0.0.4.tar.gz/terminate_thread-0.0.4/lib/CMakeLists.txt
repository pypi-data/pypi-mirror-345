cmake_minimum_required(VERSION 3.5)

project(terminate LANGUAGES C)

add_library(terminate SHARED main.c)

target_link_libraries(terminate PRIVATE pthread)


