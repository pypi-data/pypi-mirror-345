from janito.agent.tool_base import ToolBase
from janito.agent.tools_utils.action_type import ActionType
from janito.agent.tool_registry import register_tool
from janito.agent.tools_utils.utils import pluralize
from janito.i18n import tr
import os
import re
from janito.agent.tools_utils.gitignore_utils import GitignoreFilter


def is_binary_file(path, blocksize=1024):
    try:
        with open(path, "rb") as f:
            chunk = f.read(blocksize)
            if b"\0" in chunk:
                return True
            text_characters = bytearray(
                {7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100))
            )
            nontext = chunk.translate(None, text_characters)
            if len(nontext) / max(1, len(chunk)) > 0.3:
                return True
    except Exception:
        return True
    return False


@register_tool(name="search_text")
class SearchTextTool(ToolBase):
    """
    Search for a text pattern (regex or plain string) in all files within one or more directories or file paths and return matching lines. Respects .gitignore.
    Args:
        paths (str): String of one or more paths (space-separated) to search in. Each path can be a directory or a file.
        pattern (str): Regex pattern or plain text substring to search for in files. Must not be empty. Tries regex first, falls back to substring if regex is invalid.
            Note: When using regex mode, special characters (such as [, ], ., *, etc.) must be escaped if you want to match them literally (e.g., use '\\[DEBUG\\]' to match the literal string '[DEBUG]').
        is_regex (bool): If True, treat pattern as a regular expression. If False, treat as plain text (default).
            Only set is_regex=True if your pattern is a valid regular expression. Do NOT set is_regex=True for plain text patterns, as regex special characters (such as ., *, [, ], etc.) will be interpreted and may cause unexpected results.
            For plain text substring search, leave is_regex as False or omit it.
        max_depth (int, optional): Maximum directory depth to search. If 0 (default), search is recursive with no depth limit. If >0, limits recursion to that depth. Setting max_depth=1 disables recursion (only top-level directory). Ignored for file paths.
        max_results (int): Maximum number of results to return. 0 means no limit (default).
        ignore_utf8_errors (bool): If True, ignore utf-8 decode errors. Defaults to True.
    Returns:
        str: Matching lines from files as a newline-separated string, each formatted as 'filepath:lineno: line'.
        If max_results is reached, appends a note to the output.
    """

    def _prepare_pattern(self, pattern, is_regex):
        if not pattern:
            self.report_error(
                tr("Error: Empty search pattern provided. Operation aborted.")
            )
            return (
                None,
                False,
                tr("Error: Empty search pattern provided. Operation aborted."),
            )
        regex = None
        use_regex = False
        if is_regex:
            try:
                regex = re.compile(pattern)
                use_regex = True
            except re.error as e:
                self.report_warning(tr("\u26a0\ufe0f Invalid regex pattern."))
                return (
                    None,
                    False,
                    tr("Warning: Invalid regex pattern: {error}. No results.", error=e),
                )
        else:
            try:
                regex = re.compile(pattern)
                use_regex = True
            except re.error:
                regex = None
                use_regex = False
        return regex, use_regex, None

    def _search_file(
        self,
        path,
        pattern,
        regex,
        use_regex,
        max_results,
        total_results,
        ignore_utf8_errors,
    ):
        dir_output = []
        dir_limit_reached = False
        if not is_binary_file(path):
            try:
                open_kwargs = {"mode": "r", "encoding": "utf-8"}
                if ignore_utf8_errors:
                    open_kwargs["errors"] = "ignore"
                with open(path, **open_kwargs) as f:
                    for lineno, line in enumerate(f, 1):
                        if use_regex:
                            if regex.search(line):
                                dir_output.append(f"{path}:{lineno}: {line.strip()}")
                        else:
                            if pattern in line:
                                dir_output.append(f"{path}:{lineno}: {line.strip()}")
                        if (
                            max_results > 0
                            and (total_results + len(dir_output)) >= max_results
                        ):
                            dir_limit_reached = True
                            break
            except Exception:
                pass
        return dir_output, dir_limit_reached

    def _search_directory(
        self,
        search_path,
        pattern,
        regex,
        use_regex,
        max_depth,
        max_results,
        total_results,
        ignore_utf8_errors,
    ):
        dir_output = []
        dir_limit_reached = False
        if max_depth == 1:
            walk_result = next(os.walk(search_path), None)
            if walk_result is None:
                walker = [(search_path, [], [])]
            else:
                _, dirs, files = walk_result
                gitignore = GitignoreFilter()
                dirs, files = gitignore.filter_ignored(search_path, dirs, files)
                walker = [(search_path, dirs, files)]
        else:
            gitignore = GitignoreFilter()
            walker = os.walk(search_path)
        stop_search = False
        for root, dirs, files in walker:
            if stop_search:
                break
            rel_path = os.path.relpath(root, search_path)
            depth = 0 if rel_path == "." else rel_path.count(os.sep) + 1
            if max_depth == 1 and depth > 0:
                break
            if max_depth > 0 and depth > max_depth:
                continue
            dirs, files = gitignore.filter_ignored(root, dirs, files)
            for filename in files:
                if stop_search:
                    break
                path = os.path.join(root, filename)
                file_output, file_limit_reached = self._search_file(
                    path,
                    pattern,
                    regex,
                    use_regex,
                    max_results,
                    total_results + len(dir_output),
                    ignore_utf8_errors,
                )
                dir_output.extend(file_output)
                if file_limit_reached:
                    dir_limit_reached = True
                    stop_search = True
                    break
        return dir_output, dir_limit_reached

    def _format_result(self, pattern, use_regex, output, limit_reached):
        header = tr(
            "[search_text] Pattern: '{pattern}' | Regex: {use_regex} | Results: {count}",
            pattern=pattern,
            use_regex=use_regex,
            count=len(output),
        )
        result = header + "\n" + "\n".join(output)
        if limit_reached:
            result += tr("\n[Note: max_results limit reached, output truncated.]")
        self.report_success(
            tr(
                " \u2705 {count} {line_word}{limit}",
                count=len(output),
                line_word=pluralize("line", len(output)),
                limit=(" (limit reached)" if limit_reached else ""),
            )
        )
        return result

    def run(
        self,
        paths: str,
        pattern: str,
        is_regex: bool = False,
        max_depth: int = 0,
        max_results: int = 0,
        ignore_utf8_errors: bool = True,
    ) -> str:
        regex, use_regex, error_msg = self._prepare_pattern(pattern, is_regex)
        if error_msg:
            return error_msg
        paths_list = paths.split()
        results = []
        total_results = 0
        limit_reached = False
        for search_path in paths_list:
            from janito.agent.tools_utils.utils import display_path

            info_str = tr(
                "\U0001f50d Searching for {search_type} '{pattern}' in '{disp_path}'",
                search_type=("regex" if use_regex else "text"),
                pattern=pattern,
                disp_path=display_path(search_path),
            )
            if max_depth > 0:
                info_str += tr(" [max_depth={max_depth}]", max_depth=max_depth)
            self.report_info(ActionType.READ, info_str)
            dir_output = []
            dir_limit_reached = False
            if os.path.isfile(search_path):
                dir_output, dir_limit_reached = self._search_file(
                    search_path,
                    pattern,
                    regex,
                    use_regex,
                    max_results,
                    total_results,
                    ignore_utf8_errors,
                )
                total_results += len(dir_output)
                if dir_limit_reached:
                    limit_reached = True
            else:
                dir_output, dir_limit_reached = self._search_directory(
                    search_path,
                    pattern,
                    regex,
                    use_regex,
                    max_depth,
                    max_results,
                    total_results,
                    ignore_utf8_errors,
                )
                total_results += len(dir_output)
                if dir_limit_reached:
                    limit_reached = True
            # Format and append result for this path
            result_str = self._format_result(
                pattern, use_regex, dir_output, dir_limit_reached
            )
            results.append(info_str + "\n" + result_str)
            if limit_reached:
                break
        return "\n\n".join(results)
