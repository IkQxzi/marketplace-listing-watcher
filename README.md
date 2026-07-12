### Todo
***
- [x] Check if no category ID and 0 are the same
	- [x] Get category IDs
- [ ] Rewrite category ID counter and map
	- [x] Counter
	- [ ] Map
- [ ] Change category file names to category IDs (or accurate category names?)
	- [x] Active listings
	- [ ] Sold listings
- [x] Get sold listings
	- [x] Find out if `curl_cffi` is required, or if `requests` is sufficient
	- Using CamouFox
	- Could use some scraper API
 - [ ] Learn how to use Pandas from JSON files
 - [x] Check if eBay feed data (hourly data dump) is available
	 - Invite-only
 - [ ] Checkout Terapeak (visual, not API sold data)
### Params
* Skip `_trksid`, `_from`
***
`\_nkw=`: new keyword (search)
`_sacat=`: search all categories
* (`0` = full website, ID otherwise)
`_from=`: referrer,
* `R40` is referrer for using top search bar
`_trksid=`: track search ID
`p4624852.m570.l1313`
`p`: page ID
`m`: module ID
`1`: link ID
### Problem
***
**Resources**:
**Browse API:**
- Displays information about products (Price, date listed, listing ID, categories, etc.)
- Can see the top _n_ results (e.g. the top 50 items) for any search
- Can restrict searches to within a category (e.g. GPUs, Phones, etc.)
- Can do sophisticated name searching, like having lists of words where every word in the list is required in listing titles, or a list where any word in the list will do, or lists which contain words that cannot be included
- Can make 5000 API calls per day
**Sold listing webscraper:**
- Displays information about sold products (sold price, date sold, etc.)
- Does not list start date for each item
- Has all the features of regular eBay searching for sold items (essentially can do all of the above)
- Only limit is rate limit (but does not need to be polled as much, likely)\
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
***
1(a):
- [Naive] Use some statistical measure of spread, like standard deviation or variance or IQR, and combine with high turnover rate
- [Good] Use a better statistical measure; and then calculate the expected return per day. Only recommend item as profitable if return is more than a certain amount (e.g. £5) per item
additional idea: what if we used hypothesis test to calculate probability 
- [Even better] Could use lognormal distribution, better than normal - suitable for ebay prices, drop outliers (2s.d. away) and then calculate deviation, mean, etc. if anything is below 1 s.d. then good enough to sell? High turnover rate is important, could be combined with average return to calculate a threshold for whether it is useful to sell/buy said item. e.g. slightly lower turnover rate acceptable if high return
1(b): 
1(c): 
- Query top 50 items matching by name, select most frequent category. Could do multiple times just to be sure 
1(d): 
- [DONE] Best option is discord bot, all other options are either paid or convoluted. discord easy with webhooks 
2(a): 
2(b): 
- Constantly scan for new/recent listings, then if a profitable listing from our group of items is found then notify
###  Notes
***
- Could use [fieldgroups](https://developer.ebay.com/api-docs/buy/browse/resources/item_summary/methods/search#h2-samples:~:text=Occurrence%3A%20Optional-,fieldgroups,-array%20of%20string) to reduce data returned
- Checkout Notifications API
- Limit is 200 for Browse API
- Feed API (hourly data) is restricted

