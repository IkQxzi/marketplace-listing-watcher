### Todo
---
- [x] Check if no category ID and 0 are the same 
- [x] Get category IDs
	- [x] Rewrite category ID counter and map: 
	- [x] Take top-k subset to find relevant categories
- [x] Change category file names to category IDs (or accurate category nkames?)
- [ ] Get sold listings
	- [x] Find out if `curl_cffi` is required, or if `requests` is sufficient
	- Going to use some stealth browser
- [ ] Learn how to use Pandas from JSON files
- [x] Check if eBay feed data (hourly data dump) is available
- [ ] Checkout Terapeak (visual, not API sold data)
### Params
- Skip `_trksid`, `_from`
---
- `\_nkw=`: new keyword (search)
- `_sacat=`: search all categories 
	- (`0` = full website, ID otherwise)
- `_from=`: referrer,
	- `R40` is referrer for using top search bar
- `_trksid=`: track search ID 
	- `p4624852.m570.l1313`
	- `p`: page ID
	- `m`: module ID
	- `1`: link ID
### Problem
---
**Resources**:
- **Browse API:**
	- Displays information about products (Price, date listed, listing ID, categories, etc.)
	- Can see the top _n_ results (e.g. the top 50 items) for any search
	- Can restrict searches to within a category (e.g. GPUs, Phones, etc.)
	- Can do sophisticated name searching, like having lists of words where every word in the list is required in listing titles, or a list where any word in the list will do, or lists which contain words that cannot be included
	- Can make 5000 API calls per day 
- **Sold listing webscraper:**
	- Displays information about sold products (sold price, date sold, etc.)
	- Does not list start date for each item
	- Has all the features of regular eBay searching for sold items (essentially can do all of the above)
	- Only limit is rate limit (but does not need to be polled as much, likely)
**Objectives:**
	1. For a given item name:
		(a) find out if that particular item is profitable
		(b) find a way to detect when it is worth buying that item
		(c) find a way to infer the category of the item
		(d) find a way to alert when that item is listed at a good price
	2. In general:
		(a) find out which items are profitable
		(b) and a way to alert when a item worth buying is listed
### Solutions
---
- 1(a): [Naive] Use some statistical measure of spread, like standard deviation or variance or IQR, and combine with high turnover rate
- 1(a): [Good] Use a better statistical measure; and then calculate the expected return per day
- 1(b):
- 1(c):
- 1(d):
- 2(a):
- 2(b) 
### Notes
---
- Could use [fieldgroups](https://developer.ebay.com/api-docs/buy/browse/resources/item_summary/methods/search#h2-samples:~:text=Occurrence%3A%20Optional-,fieldgroups,-array%20of%20string) to reduce data returned 
- Notifications API
- **Used:**
	- Memory
- Limit is 200 for Browse API