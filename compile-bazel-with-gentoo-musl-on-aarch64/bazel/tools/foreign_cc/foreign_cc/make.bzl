# tools/cmake/foreign_cc/make.bzl

def make(*args, **kwargs):
    # dummy placeholder for Bazel loading
    print("Stub make called with", kwargs.get("name", "<unknown>"))

__all__ = ["make"]

