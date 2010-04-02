def locate(pattern, root):
    """
    Utility function to walk a directory locating files that match a pattern.
    """
    import os
    from fnmatch import fnmatch
    
    for path, dirs, files in os.walk(root):
        for filename in [os.path.join(path, filename) for filename in files if
                         fnmatch(filename, pattern)]:
            yield filename
