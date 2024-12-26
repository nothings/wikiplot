# wikiplot
python scripts for extracting plot summaries from English wikipedia

# Usage

## Download XML

1. Go to https://dumps.wikimedia.org/ or a mirror found on that page
2. Go to "database backup dumps"
3. Find the log entry that says "enwiki", and click it
4. Find the section labeled "Recombine articles, templates, media/file descriptions, and primary meta-pages."
5. If it's not "done", go the top of the page, and click on "Last dumped on" to get an older, completed dump
6. Download the "enwiki-DATE-pages-articles.xml.bz2" file, currently 20 GB
7. Unpack it, giving an XML file (currently 90 GB)

## Customize scripts

The processing is broken into two steps. The first step, `wikiplot_1`, extracts all the articles with something resembling a `Plot` section into a temporary file, `wikiplots_db.txt`. The second step does the actual processing. The first step is slow since it processes a (currently) 90 GB XML file; the second step is much quicker, since `wikiplots_db.txt` is currently 0.5 GB.

### wikiplot_1.py

1. Set the correct path and name of your XML file
2. Set `omit_foreign` to `True`/`False` based on your preference

### wikiplot_2.py

1. Set the correct output directory for the wikiplot files
2. Set `summaries_per_html_file` as desired

## Run scripts

1. Run 'wikiplot_1.py' to create `wikiplots_db.txt`. This will take a while to parse the ~90 GB XML file and extracts all the `Plot` sections of all articles with them.
2. Run 'wikiplot_2.py' to process `wikiplots_db.txt`, creating the final HTML output
