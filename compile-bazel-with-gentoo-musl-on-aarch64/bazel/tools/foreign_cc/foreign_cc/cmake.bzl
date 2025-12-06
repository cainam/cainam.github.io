def cmake(name, **kwargs):
    print("Using local cmake stub for", name)
    native.genrule(
        name = name,
        outs = ["{}.stamp".format(name)],
        # Just echo something to make Bazel happy; no $(location) on absolute paths
        cmd = "echo Using local cmake stub for {} > $@".format(name),
    )

