import mistletoe
import re
import subprocess
import tempfile
import contextlib
import os
import logging
import collections


logger = logging.getLogger("aimo")

code_blocks = [mistletoe.block_token.CodeFence, mistletoe.block_token.BlockCode]


def get_text(child):
    if hasattr(child, "children"):
        return "\n".join(map(get_text, child.children))
    elif hasattr(child, "content"):
        return child.content
    return ""


def parse_output(raw_output):
    doc = mistletoe.Document(raw_output)
    code_chunks = []
    texts = []
    for i, child in enumerate(doc.children):
        if any(isinstance(child, code) for code in code_blocks):
            code_chunks.append(
                {"id": i, "language": child.language, "code": child.content}
            )
        else:
            texts.append({"id": i, "text": get_text(child)})

    return {"code_chunks": code_chunks, "texts": texts}


def boxed_answer(text):
    answers = re.findall(r"\\(?:framebox|boxed|fbox)\{(.*?)\}", text)
    return answers[-1] if answers else ""


@contextlib.contextmanager
def new_tempfile():
    try:
        fd, fname = tempfile.mkstemp(suffix=".py")
        os.close(fd)
        logger.info("temp file: %s", fname)
        yield fname
    finally:
        if os.path.exists(fname):
            os.unlink(fname)
            logger.info("temp file %s to be deleted", fname)


def run_code_chunk(chunk, timeout=7):
    with new_tempfile() as code_file:
        with open(code_file, "w") as f:
            f.write(chunk)

        logger.info("running python3 on \n```\n%s\n```", chunk)

        try:
            result = subprocess.run(
                ["python3", code_file], timeout=timeout, capture_output=True
            )
        except subprocess.TimeoutExpired:
            logger.info("timeout occured")
            return ""

        if result.returncode:
            logger.info("error occured %s", result.stderr.decode("utf8"))
            return ""

        stdout = result.stdout.decode("utf8")
        logger.info("output: %s", stdout)

        return stdout


def get_answers(raw_outputs):
    answers = collections.Counter()

    def add(ans):
        try:
            answers[int(ans) % 1000] += 1
        except ValueError:
            pass

    for raw_output in raw_outputs:
        blocks = parse_output(raw_output)
        for chunk in blocks["code_chunks"]:
            if chunk["language"] == "output":
                ans = chunk["code"].strip()
            elif chunk["language"] in ("python", ""):
                ans = run_code_chunk(chunk["code"])
            add(ans)

        if blocks["texts"]:
            add(boxed_answer(blocks["texts"][-1]['text']))

    return answers


def get_answer(raw_outputs):
    answers = get_answers(raw_outputs)
    if answers:
        return answers.most_common(1)[0][0]
    else:
        return 0
