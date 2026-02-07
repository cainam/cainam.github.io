# tools/foreign_cc/foreign_cc/defs.bzl
def xxcc_library(*args, **kwargs):
    """Replacement for foreign_cc rules that defines an empty native cc_library."""
    name = kwargs.get("name", "<unknown>")
    # Call the native cc_library function to define a real Bazel target
    include_paths = ["/opt/libevent/include","/usr/local/include"]
    native.cc_library(
        name = name,
        srcs = [],
        hdrs = [],
        deps = [],
        # You may need to add include directories if your locally installed
        # libraries aren't found by default, e.g., if installed to /usr/local
        # includes = ["/usr/local/include"],
        # If linking is needed, you may need to specify linkopts.
        # linkopts = ["-l" + name], # Only if you have a locally installed .so/.a
        includes = include_paths, 
	copts = ["-isystem", "/usr/local/include"] 
    )
    print("Stub cc_library called and defined native target:", name)


def cc_library(**kwargs):
    name = kwargs.get("name", "<unknown>")
    native.cc_library(
        **kwargs
    )
    print("Stub cc_library called and defined native target:", name)

# ... keep make and cmake definitions as stubs if they are used to call cc_library internally ...
def make(*args, **kwargs):
    print("Stub make called with", kwargs.get("name", "<unknown>"))
    cc_library(*args, **kwargs) # Call cc_library if 'make' is a wrapper

def cmake(*args, **kwargs):
    print("Stub cmake called with", kwargs.get("name", "<unknown>"))
    cc_library(*args, **kwargs) # Call cc_library if 'cmake' is a wrapper

__all__ = ["cc_library", "make", "cmake"]
