wuxia-scraper
===========

A basic python scraper used for wuxiaworld.com to generate pdfs from stories. 

The scraping functionality currently works on books that:
* use urls formatted like /{book_index}-index/{book_chapter}-chapter-{number}/ 
* use a single \<hr> tag before the main text of each chapter

The scraper can optionally send the generated pdfs to a kindle through email where it gets converted to the kindle format


