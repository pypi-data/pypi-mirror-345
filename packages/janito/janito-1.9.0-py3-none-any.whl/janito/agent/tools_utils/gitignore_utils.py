import os
import pathspec

_spec = None


def load_gitignore_patterns(gitignore_path=".gitignore"):
    global _spec
    if not os.path.exists(gitignore_path):
        _spec = pathspec.PathSpec.from_lines("gitwildmatch", [])
        return _spec
    with open(gitignore_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    _spec = pathspec.PathSpec.from_lines("gitwildmatch", lines)
    return _spec


def is_ignored(path):
    global _spec
    if _spec is None:
        _spec = load_gitignore_patterns()
    # Normalize path to be relative and use forward slashes
    rel_path = os.path.relpath(path).replace(os.sep, "/")
    return _spec.match_file(rel_path)


def filter_ignored(root, dirs, files, spec=None):
    if spec is None:
        global _spec
        if _spec is None:
            _spec = load_gitignore_patterns()
        spec = _spec

    def not_ignored(p):
        rel_path = os.path.relpath(os.path.join(root, p)).replace(os.sep, "/")
        # Always ignore .git directory (like git does)
        if rel_path == ".git" or rel_path.startswith(".git/"):
            return False
        return not spec.match_file(rel_path)

    dirs[:] = [d for d in dirs if not_ignored(d)]
    files = [f for f in files if not_ignored(f)]
    return dirs, files
