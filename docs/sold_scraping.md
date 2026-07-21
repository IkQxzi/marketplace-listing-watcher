### Sold URL main structure
---
- `\_nkw`: new keyword (search)
- `_ex_kw`: words to exclude
- `_sacat`: category to search
	* `0` = full website
	* ID otherwise (use tree)
- `LH_Sold`: show sold listings
	- `1`: true
- `LH_Complete`: show completed listings (ended without bid/failed)
	- `1`: truek
- `_ItemCondition`:
	- `1000`: new
	- `3000`: used
- `_sop`: sort by
	- `7`: closest first
	- `10`: ended recently
	- `15`: lowest price + P&P
	- `16`: highest price + P&P
- `_udlo`: lowest price
	- supports float
- `_uhhi`: highest price
	- supports float
- `_ipg`: results per page
	- `60`, `120` or `240`
	- Round to nearest when implemented (with warning)
- `LH_PrefLoc`: location preference
	- `98`: default
	- `1`: UK Only
	- `2`: Worldwide
	- `3`: European Union
	- `6`: Continental Europe
#### Sold URL Secondary structure
---
`_from`: referrer,
* `R40` is referrer for using top search bar
`_trksid`: track search ID
`p4624852.m570.l1313`
`p`: page ID
`m`: module ID
`1`: link ID
