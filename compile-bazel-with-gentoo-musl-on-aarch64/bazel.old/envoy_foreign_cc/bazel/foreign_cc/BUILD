cc_library(
    name = "liburing",
    srcs = [],
    hdrs = [],
)

cc_library(
    name = "liburing_linux",
    srcs = [],
    deps = select({
        "//bazel:linux": [":liburing"],
        "//conditions:default": [],
    }),
)
