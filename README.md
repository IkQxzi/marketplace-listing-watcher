# marketplace-listing-watcher: A zero-knowledge tool for finding good product deals from eBay first
A tool which enables users to setup watchers of specific products with 0 knowledge about them, and be notified when new deals are listed. 

# Outline
1. Setup filters for a product:
    - A watcher for a product requires filters to keep out junk and disingenuous listings
    - The hypothesis here is that setting up filters should be zero-knowlege 
    - For example, ou should not need to know that an unintended side effect of searching 'iphone 18' is that many other iphone variants (the Pro/Max models, other generations, etc.) will come up in the results.
    - To enable this, the tool uses a LLM to generate precise filters for a search given to it in natural language.
    - For example, 'iphone 18 pro' will result in filters that automatically remove the '18 pro max', '18 air', and other variants, generations, and generally anything unwanted in the results.
    - The tool combines this with statistical filters after listings are retrieved to remove outliers.
    - The overall effect should be that only listings you would have intended to view on the eBay site will be returned.
2. 

# Scripts
**HTML to CSV converter**
- Usage: `html2csv path/to/html/file item_name`
- See `scripts/html2csv.py` for more details
