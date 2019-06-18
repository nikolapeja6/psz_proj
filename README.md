# psz_proj

## Requirements

In order to run the code, you need to have [Python 3.x][python3] installed.

You will also need the following python packages:
 - requests
 - beautifulsoup4
 - fuzzywuzzy
 - python-Levenshtein 
 - regex
 - matplotlib
 - numpy
 - cyrtranslit
 - scikit-learn
 - bokeh


## Scraping data from the pages

The data on the pages can be structured differently, which caused me some difficulties when I tried to scrape it.
Below are some examples of the pages with different structures.

 - Albums
   - [versions; tracklist with times but no credits](https://www.discogs.com/Bob-Dylan-Self-Portrait/master/28188)
   - [tracklist with some addition labels but no times](https://www.discogs.com//Mile-Delija-%D0%9E%D1%98-%D0%A1%D1%80%D0%B1%D0%B8%D1%98%D0%BE-%D0%9C%D0%B0%D1%98%D0%BA%D0%BE-%D0%9D%D0%B5-%D0%9F%D0%BB%D0%B0%D1%88%D0%B8-%D0%A1%D0%B5-%D0%A0%D0%B0%D1%82%D0%B0/release/7347664)
   - [tracklist with credits but no times; album credits](https://www.discogs.com/Various-4-Uspjeha-Sa-Festivala-Sanremo-1960/release/3722600)
   - [tracklist with credits and times; album credits](https://www.discogs.com//Various-Radio-Utopia-4-Belgrade-Coffee-Shop/release/142792)
   - [tracklist with no additional data; album credits](https://www.discogs.com//Radioaktivni-Radioaktivni/release/4009346)
   - [tracklist with no link to songs but with credits](https://www.discogs.com//To%C5%A1e-Proeski-Pratim-Te/release/5006269)
   - [additional separators in the tracklist](https://www.discogs.com/Dragi-Domi%C4%87-Boem-Grada/release/13675687)
 - Artists
   - [artist with aliases, sites and metrics](https://www.discogs.com/artist/59792-Bob-Dylan)
   - [artist with no sites, some mestrics](https://www.discogs.com/artist/2984842-Dragi-Domi%C4%87)
 - Songs
   - [album with no credits for song](https://www.discogs.com//Radioaktivni-Radioaktivni/release/4009346) => [song with credits](https://www.discogs.com/composition/2bf9dd96-7837-415f-9318-495cee3d9fe4-Ne-Pri%C4%8Daj)
   - [album with some credits for song](https://www.discogs.com//Various-Radio-Utopia-4-Belgrade-Coffee-Shop/release/142792) => [song with different credits](https://www.discogs.com/composition/0604c137-ac24-4f15-9d4b-61b551912a93-Svitac)
   - [album with credits for songs](https://www.discogs.com/To%C5%A1e-Proeski-Secret-Place/release/12749465) => [sogn with no credits](https://www.discogs.com/composition/c61866a0-b099-4d84-9a78-399a68ef4844-Light-The-Flame)

[python3]: https://www.python.org/downloads/