import argparse
import json
import re
import shlex
import textwrap

header_parser = argparse.ArgumentParser()
header_parser.add_argument("--no-output", default=False, action="store_true")
header_parser.add_argument("--discard", default=False, action="store_true")
header_parser.add_argument("--output-only", default=False, action="store_true")


def apply_header(header, cell):
    if header.discard:
        return None
    if header.no_output and not global_args.keep_output:
        cell["outputs"] = []
    if header.output_only:
        cell = dict(
            cell_type="markdown",
            metadata={},
            source=outputs_to_markdown(cell["outputs"]),
        )

    return cell


line_parser = argparse.ArgumentParser()
line_parser.add_argument("--remove-below", default=False, action="store_true")
line_parser.add_argument("--remove-until")

_leading_whitespace = re.compile(r"^([ \t]*)([^ \t].*)")


def apply_line(args, i, lines):
    matches = [_leading_whitespace.match(line) for line in lines]
    indents = [match.group(1) if match is not None else None for match in matches]
    contents = [match.group(2) if match is not None else None for match in matches]
    if args.remove_below:
        j = i + 1
        to_reverse = 0
        while j < len(indents) and (
            indents[j] is None or len(indents[j]) >= len(indents[i])
        ):
            if indents[j] is None:
                to_reverse += 1
            else:
                to_reverse = 0
            j += 1
        j -= to_reverse
        del lines[i:j]
    if args.remove_until:
        j = i + 1
        to_reverse = 0
        while j < len(indents) and (
            indents[j] is None or len(indents[j]) >= len(indents[i])
        ):
            if indents[j] is None:
                to_reverse += 1
            else:
                to_reverse = 0
            if contents[j] == args.remove_until:
                j += 1
                break
            j += 1
        j -= to_reverse
        if args.remove_until in global_args.dont_remove:
            del lines[i]
        else:
            del lines[i:j]

    return lines


def outputs_to_markdown(outputs):
    markdown = []
    for output in outputs:
        if output["output_type"] == "display_data" and "image/png" in output["data"]:
            markdown.append(
                "<img src='data:image/jpeg;base64,{}' />".format(
                    output["data"]["image/png"]
                )
            )
        elif output["output_type"] == "stream":
            if output["name"] == "stdout":
                markdown.append("<pre>{}</pre>".format("".join(output["text"])))
            elif output["name"] == "stderr":
                markdown.append(
                    "<pre style='color:red;'>{}</pre>".format("".join(output["text"]))
                )
            else:
                raise NotImplementedError(output["name"])
        else:
            raise NotImplementedError(output["output_type"])

    return "".join(markdown)


def process_lines(source):
    lines = list(source)
    i = 0
    while i < len(lines):
        line = lines[i]
        line = textwrap.dedent(line)
        if line.startswith("#%"):
            options = line_parser.parse_args(shlex.split(line[2:]))
            lines = apply_line(options, i, lines)
        i += 1

    return lines


def process_cell(cell):
    if cell["cell_type"] != "code":
        return cell

    source = cell["source"]
    if source and source[0].startswith("#%%"):
        header = header_parser.parse_args(shlex.split(source[0][3:]))
        source = source[1:]
    else:
        header = header_parser.parse_args(())

    cell["source"] = source
    cell["execution_count"] = None
    cell = apply_header(header, cell)

    if cell is not None:
        lines = "".join(cell["source"]).replace("\r\n", "\n").split("\n")
        lines = process_lines(lines)
        lines = [line + "\n" for line in lines[:-1]] + lines[-1:]
        cell["source"] = lines

    return cell


def handle_cells(cells):
    for cell in cells:
        result = process_cell(cell)
        if isinstance(result, dict):
            yield result
        if isinstance(result, list):
            yield from result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--output-file", default="_student")
    parser.add_argument("--keep-output", default=False, action="store_true")
    parser.add_argument("--dont-remove", default=(), type=lambda x: x.split(","))

    args = global_args = parser.parse_args()

    with open(args.file) as file:
        notebook_code = file.read()
    nb = json.loads(notebook_code)
    nb["cells"] = list(handle_cells(nb["cells"]))
    filename = args.file[:-6] + args.output_file + args.file[-6:]
    print(filename)
    with open(filename, "w") as file:
        file.write(json.dumps(nb, indent=2))
    print(nb["cells"][0])
