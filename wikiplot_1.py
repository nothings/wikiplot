source_file = 'G:/wikipedia/enwiki-20220820-pages-articles/enwiki-20220820-pages-articles.xml'

omit_foreign = True
# This generally allows English-speaking films from USA, UK, Australian,
# and New Zealand, which maybe seems racist in what it excludes, but I
# found it generally raised the quality of the results, at least for my
# purposes. Your experience may vary.

foreign = [ "Pakistani", "Indian", "Chinese", "Hindi" ]
# pages are assumed to be "foreign" if the beginning of the
# article contains "English:" (normally used to indicate
# a translation of the original name to English) or any
# of the above words (determined experimentally)

import xml.etree.ElementTree as ET
import re
import os

out = open("wikiplots_db.txt", "w", encoding="utf-8")

cur_title = ""
count = 0

def process_element(text):
    if not isinstance(text,str):
        return

    # strip comments
    temp = re.split(r"<!--.*-->",text)
    text = "".join(temp)

    # find section headers
    result = re.split(r"(==.*==)[ ]*\n", text)
    for i in range(1,len(result),2):
        x = result[i]

        # remove '=' prefix, but count how many there are
        x = x.lstrip("=")
        equal_count = len(result[i]) - len(x)
        x = x.lstrip(" ")

        # if the first 4 characters are "Plot", assume it's got a plot summary;
        # this will be validated in wikiplot_2.py, which is much faster so easier
        # to tune
        if x[:4] == "Plot":
            header = text[:1250]
            if omit_foreign and ("English:" in header or any(x in header for x in foreign)):
                pass
            else:
                global count
                count += 1
                print(f"= TITLE: {cur_title} =", file=out)
                print(header, file=out) # save the header for further processing, currently unused
                print(f"= ENDHEADER =", file=out)
                print(result[i], file=out)
                print(result[i+1], file=out)
                equal_count += 1
                more_eq = "=" * equal_count
                for j in range(i+2,len(result),2):
                    if result[j][0:equal_count] == more_eq:
                        print(result[j], file=out)
                        print(result[j+1], file=out)
                    else:
                        break

tree = []

last_count = count

for event, elem in ET.iterparse(source_file, events=('start', 'end')):
    if count >= last_count + 100:
        last_count = count
        print(f"{count}\r", end="")

    if event == 'start':
        tree.append(elem.tag.split("}")[1])
    elif event == 'end':
        if   tree[:4] == [ "mediawiki", "page", "title" ]:
            cur_title = elem.text
        elif tree[:4] == [ "mediawiki", "page", "revision", "text" ]:
            try:
                process_element(elem.text)
            except Exception as e:
                print(f"Error: {e}")
        tree.pop()
        elem.clear()  # discard to reduce memory usage

out.close()

print(f"Found {count} candidates.")
