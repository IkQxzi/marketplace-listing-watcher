_Describes the structure of saved eBay sold-listing pages as of August 2026._

### HTML Structure
---
- **Delivery information**
	- Classes:
		- For the price ('+11.95'), 3 classes: `su-styled-text`, `secondary`, `large`
		- For the following string, 3 classes: `su-styled-text`, `positive`, `bold`, `large`
	- Variations:
		- "Free Delivery" always when free
		- "+11.95 delivery in 2-3 days"
		- "+2.95 delivery"
			- Note that regex matching may be insufficient as some listing titles advertise "free delivery"
			- Could do exact regex matching (exact capitalisation, '+' symbol)
### Sold URL main structure
---
**searching:**
- `_nkw`: words to search for
	- Can also be item ID
	- Defaults to 'all words, any order'
- `_in_kw`: how to look for the words in `_nkw`
	- (unspecified): any words, any order: every word, any sequence
	- `2`: any words, any order: only one word from the search is required
	- `3`: exact words, exact order: the exact search phrase is required
	- `4`: exact words, any order: all words must appear, but can be in any order
- `_ex_kw`: words to exclude
- `_sacat`: category to search
	* `0` = full website
	* ID otherwise (use tree)
* `LH_TitleDesc`: include title **& description** in search
	* `1`: true
- `_ipg`: results per page
	- `60`, `120` or `240`
	- Round to nearest when implemented (with warning)
**condition:** 
- `_ItemCondition`:
	- `1000`: new
	- `3000`: used
**price:**
- `_udlo`: lowest price
	- supports float
- `_uhhi`: highest price
	- supports float
**show only:**
- `LH_Sold`: show sold listings
	- `1`: true
- `LH_Complete`: show completed listings (ended without bid/failed)
	- `1`: truek
**sort:** 
- `_sop`: sort by
	- `7`: closest first
	- `10`: ended recently
	- `15`: lowest price + P&P
	- `16`: highest price + P&P
**location:**
- `LH_PrefLoc`: location preference
	- `98`: default
	- `1`: UK Only
	- `2`: Worldwide
	- `3`: European Union
	- `6`: Continental Europe
#### Sold URL Secondary structure
---
- `_from`: referrer,
	* `R40` is referrer for using top search bar
- `_trksid`: track search ID
	- e.g. `p4624852.m570.l1313`
	- `p`: page ID
	- `m`: module ID
	- `1`: link ID
