add_library(js
    pxr/js/json.cpp
    pxr/js/utils.cpp
    pxr/js/value.cpp
)

target_include_directories(js
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

target_link_libraries(js
    PUBLIC
        pxr::arch
        pxr::tf
)

if (ENABLE_PRECOMPILED_HEADERS)
    target_precompile_headers(js
        PRIVATE
            pxr/js/pch.h
    )
endif()

set_target_properties(js
    PROPERTIES
        POSITION_INDEPENDENT_CODE ON
        OUTPUT_NAME "PxrJs"
)

target_compile_definitions(js
    PRIVATE
        JS_EXPORTS=1
        MFB_PACKAGE_MODULE=Js
        MFB_PACKAGE_NAME=js
        MFB_ALT_PACKAGE_NAME=js
)

install(
    TARGETS js EXPORT ${PROJECT_NAME}
    RUNTIME DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(
    FILES
        pxr/js/api.h
        pxr/js/converter.h
        pxr/js/json.h
        pxr/js/pch.h
        pxr/js/types.h
        pxr/js/utils.h
        pxr/js/value.h
    DESTINATION
        ${CMAKE_INSTALL_INCLUDEDIR}/pxr/js
)

install(EXPORT ${PROJECT_NAME}
    FILE pxr-js-targets.cmake
    NAMESPACE pxr::
    DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/pxr-js
)