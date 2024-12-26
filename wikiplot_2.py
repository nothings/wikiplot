output_path = 'g:/wikiplot'
summaries_per_html_file = 200

import xml.etree.ElementTree as ET
import re
import os
import markdown

with open("wikiplots_db.txt", "r", encoding="utf-8") as out:
    text = out.read()

plots = {}

articles = re.split(r"\n= TITLE: (.*) =\n", text)

output = []
filenum = 0

def process(text, title):
    if text.strip() == "":
        return ""

    debug = False

    # match {{blockquote|...}}
    segments = re.split(r"({{|}})", text)
    i=1
    depth = 0
    start = 1
    while i < len(segments):
        if debug:
            print("    0: " + segments[i-1][:40])
            print("    1: " + segments[i][:40])
        if segments[i] == "{{":
            if depth==0:
                start = i
            depth += 1
            
        if segments[i] == "}}":
            depth -= 1
            if depth == 0:
                if segments[start+1].startswith("blockquote|"):
                    if debug: print("    " + segments[start+1][:20])
                    # rewrite as a non-blockquote
                    segments[start+0] = ""
                    segments[start+1] = segments[start+1][11:]
                    segments[i      ] = ""

        i += 2
    text = "".join(segments)

    # strip {} sections inside-out
    segments = re.split(r"({|})", text)
    i=1
    while i+3 < len(segments):
        if segments[i] == "{" and segments[i+2] == "}":
            segments = segments[0:i-1] + [ segments[i-1]+" "+segments[i+3] ] + segments[i+4:]
            if i >= 3:
                i -= 2
        else:
            i += 2
    text = " ".join(segments)

    # replace single hashes with *
    segments = re.split(r"\n# ", text)
    if len(segments) != 1:
        for i in range(1,len(segments)):
            s = "\n* " + segments[i]
            if "\n" in segments[i-1][2:]:
                s = "\n" + s
            segments[i] = s

    text = "".join(segments)

    # replace === foo === with hashes
    segments = re.split(r"\n(=+.*=+)\n", text)
    for i in range(1,len(segments),2):
        s = segments[i]
        s = s.rstrip("=")
        s = s.replace("=", "#")
        segments[i] = "\n"+s+"\n"
    text = "".join(segments)

    # replace [[ | ]] with plain text
    segments = re.split("(\[\[|\]\]|[|])", text)
    i = 1
    while i+2 < len(segments):
        if segments[i] == "[[":
            nest = 0
            j = i + 2
            while j+2 < len(segments) and (segments[j] != "]]" or nest > 0):
                if segments[j] == "]]":
                    nest -= 1
                elif segments[j] == "[[":
                    nest += 1
                j += 2

            if segments[j] == "]]":
                if segments[i+1][:4] == "File":
                    segments = segments[:i] + [""] + segments[j+1:]
                else:
                    segments = segments[:i] + [segments[j-1]] + segments[j+1:]
                if i > 1:
                    i -= 2
            else:
                i += 2
        else:
            i += 2
    text = "".join(segments)

    # strip <ref>...</ref>
    #   *? is ungreedy, avoids matching first <ref> to last </ref>
    segments = re.split(r"<ref>.*?</ref>", text)

    # todo: this is untested, but should fix bugs
    #   (?s:.) matches any character, including newline
    #segments = re.split(r"<ref>(?s:.)*?</ref>", text)
    text = "".join(segments)

    # just rely on utf-8 instead of manually converting characters
    # text = text.replace(chr(8211), "&ndash;")
    # text = text.replace(chr(8212), "&mdash;")

    return markdown.markdown(text)

def writefile():
    global output,filenum
    filename = os.path.join(output_path,  f"wikiplot_{filenum:03}.html")
    with open(filename,"w",encoding="utf8") as f:
        print(f"<html><head><title>wikiplot_{filenum:03}.html</title><meta charset='UTF-8'></head><body>\n", file=f)
        print("From Wikipedia under the Creative Commons Attribution-ShareAlike License\n<p><hr>", file=f)
        print("\n<hr>\n".join(output), file=f)
    print(f"Wrote {filename}")
    output = []
    filenum += 1

for i in range(1,len(articles),2):
    title = articles[i]
    parts = re.split(r"\n= ENDHEADER =\n", articles[i+1], maxsplit=1)
    header = parts[0]
    sections = re.split(r"=+ *(Plot.*)=+\n", parts[1], maxsplit=1)
    if len(sections) > 2:
        k = sections[1]

        # strip various trailing characters
        k = k.rstrip("\n")
        k = k.rstrip("=")
        k = k.rstrip(" ")
        k = k.rstrip(".")
        k = k.rstrip(":")

        # whitelist various spellings of "== Plot summary =="
        if k.lower() in ["plot summary", "plot", "plot overview", "plot outline",
                           "plotline", "plotlines", "plot synopsis", "plot synopses",
                           "plot sumary", "plot and story", "plot/synopsis", "plot basics",
                           "plot (synopsis)", "plot and summary"
                          ]:
            pass
        elif k.startswith("Plot summary") or k == "Plot  Summary":
            pass
        else:
            continue

        html = process(sections[2], title)

        if (html == ""):
            continue

        output.append(f"<div align=right><small>{title}</small></div>\n" + html)
        if len(output) >= summaries_per_html_file:
            writefile()
    else:
        print("INVALID: ", parts[1][:1000])

writefile()