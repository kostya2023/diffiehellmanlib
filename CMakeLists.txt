cmake_minimum_required(VERSION 3.14)
project(diffiehellmanlib)

set(TARGET_LIB_NAME "diffiehellmanlib")
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(OpenSSL REQUIRED)

set(SOURCES diffiehellmanlib/src/utils.cpp)

add_library(${TARGET_LIB_NAME} SHARED ${SOURCES})

target_link_libraries(${TARGET_LIB_NAME} PRIVATE OpenSSL::Crypto)

target_include_directories(${TARGET_LIB_NAME} PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/diffiehellmanlib/src>
)

if (WIN32)
    set_target_properties(${TARGET_LIB_NAME} PROPERTIES
        OUTPUT_NAME "${TARGET_LIB_NAME}"
        SUFFIX ".dll"
    )
elseif(APPLE)
    set_target_properties(${TARGET_LIB_NAME} PROPERTIES
        OUTPUT_NAME "${TARGET_LIB_NAME}"
        SUFFIX ".dylib"
    )
else()
    set_target_properties(${TARGET_LIB_NAME} PROPERTIES
        OUTPUT_NAME "${TARGET_LIB_NAME}"
        SUFFIX ".so"
    )
endif()

# Указываем, куда устанавливать библиотеку
install(TARGETS ${TARGET_LIB_NAME} DESTINATION diffiehellmanlib)
install(FILES diffiehellmanlib/src/utils.h DESTINATION diffiehellmanlib/include)