# marketplace-listing-watcher: A zero-knowledge tool for finding good product deals from eBay first
A tool which enables users to setup watchers of specific products with no knowledge about them, and be notified when new deals are listed. 

> [!NOTE]
> This tool is a work-in-progress. See [Project Status](#project-statusroadmap) for more details.

# Quick Links
- [Outline](#outline)
- [Requirements](#requirements)
- [Configuration](#configuration)
    - [API Keys](#api-keys)
- [Usage Guide](#usage-guide)
    - [Setting Up Filters](#setting-up-filters)
    - [Configuring Alerts](#configuring-alerts)
- [Project Status/Roadmap](#project-statusroadmap)
    - [Known Issues](#known-issues)
- [Methodology](#methodology)
    - [Filters](#filters)
        - [LLM Filter Generation](#llm-filter-generation)
    - [Identifying Deals](#identifying-deals)
        - [User Data Method](#user-data-method)
        - [Active Listing Method](#active-listing-method)
    - [Alerts](#alerts)
- [Handy Scripts](#handy-scripts)
- [Disclaimers](#disclaimers)
- [License](LICENSE)

## Outline
1. Describe a product in natural language:
    - Filters are automatically generated from a description, for example 'iPhone 17 base model', or 'RTX 5060 Ti 16GB'.
2. Retrieve new listings:
    - The tool uses the filters from the previous steps to request only relevant listings from the eBay site, and saves them to a database on the local disk.
3. Generate alerts (if applicable):
    - If any listings match the criteria for a "good deal", an alert is sent to the user.
4. Repeat:
    - The tool saves the filters generated in the first step, and continuously polls the API for new listings[^1]

[^1]: According to your API key limits.


## Requirements
- [uv package manager for Python][1]
- App ID, Cert ID from the [eBay Developer portal](https://developer.ebay.com/)
- [Discord Bot webhook URL][2]
- Some LLM API Key

## Configuration
### API Keys
- eBay (production) API keys from [developer dashboard][3]:
    - App ID (Production)
    - Cert ID (Production)
    - Refresh token (Production)
- Discord Webhook URL
- Gemini API key (for filter generation)
- See .env.example for key naming format

## Usage Guide
### Installation
- Run `git clone https://github.com/ikqxzi/marketplace-listing-watcher`
- Run `uv tool install -e .` to install all packages and add the CLI
- For most users, automatic filters are recommended. See [Setting Up Filters](#setting-up-filters) for more.

### Usage
- `mlw watch [flags] [args]`
- See `mlw watch --help` for more info

### Example usage
- `mlw watch -g "used ps5 under 500"`
    - Output: Filter for only new used ps5 consoles, excluding non-console listings, upper price cap of 500, reasonable lower price cap
- `mlw watch -g "existing iphone 18"`
    - Output: Filter for active iphone 18s at any price, assuming base model (excluding Pro/Max lineup).
- `mlw watch -g "samsung s24 ultra" -d 1000`
    - Will only poll up to 1000 times per day (up from the default 5000)

### Notes
- The default daily limit (set by `-d|--daily-limit`) defaults to 5000, the limit for one API key. Adjust accordingly.
- The watcher now run constantly, polling the API as often as the API key limit is set.
- Note that the filters default to return only new listings.
- Mention "existing" in the natural language description to return active listings.

### Setting Up Filters
- Currently, there are three types of filters supported: automatic filters, simplified filters, and full (manual) filters.
- Filters are per-watcher-call, meaning they do not automatically persist across sessions. This will be implemented in future.
**Automatic filters:**
- Use with `mlw -g [natural language description]`
**Simplified filters:**
- See `filters/template.yml` for a template and explanation of options
- Use with `mlw -s [yaml_path]`
**Full filters:**
- Currently no templates, work-in-progress.
- Use with `mlw -j [json_path]`

### Configuring Alerts
- Currently alerts for all new listings. Therefore, you should 
- Work in Progress. Will be updated soon.

### Obtaining Your Own Data
- Work in Progress. Will be updated soon.
- There are two ways to use this tool: with your own data, or with the active listings retrieved by previous use. (See [Identifying Deals](###identifying-deals) for more detail.)

## Project Status/Roadmap
- This tool is a work-in-progress. It is missing many key features. See below for which features are implemented, which have some progress, and which are missing completely.
- RA[G]: Filters
    - [x] Implemented as Pydantic classes
    - [x] Can be manually created from entry point
    - [x] LLM used to generate filters from natural language
- R[A]G: Data Retrieval
    - [x] API polled for listings
    - [x] Polling done on a constant loop
    - [ ] Deals identified by statistics from database
- R[A]G: Data Storage
    - [x] Active listings saved to disk 
        - _currently .jsonl files_
    - [ ] SQL Database used for storage
- R[A]G: Alerts
    - [x] Interface for alerts to be sent to Discord
    - [ ] Configuration options to define thresholds/conditions for alerts
- R[A]G: User Interface
    - [x] CLI entry point 
    - [ ] Improved CLI (separate generate command)
    - [ ] CLI tools (update-refresh-token, parsing)

### Known Issues
- For very precise restrictions - those that may not return any currently active listings - the payload quality may not be as good as hoped, simply because there are no results for the LLM to validate its generated payload against.
- Logging - the CLI just spews out logs, will fix at some point.

## Methodology

### Filters
---
#### Overview
- A watcher for a product requires filters to keep out junk, and disingenuous listings.
- The hypothesis here is that setting up filters should be zero-knowlege.
- For example, you should not need to know that an unintended side effect of searching 'iphone 18' is that many other iphone variants (the Pro/Max models, other generations, etc.) will come up in the results.
- To enable this, the tool uses a LLM to generate precise filters for a search given to it in natural language (see next section).
- For example, 'iphone 18 pro' will result in filters that automatically remove the '18 pro max', '18 air', and other variants, generations, and generally anything unwanted in the results.
- The tool combines this with statistical filters after listings are retrieved to remove outliers.
- The overall effect *should* be that only listings you would have intended to view on the eBay site will be returned, but it is impossible to guarantee this with 100% certainty, so keep this in mind when acting on the statistics produced by this tool.

#### LLM Filter Generation
- Work in progress. Many features missing or incomplete.

### Identifying Deals
---
- It is only really useful to be notified of good deals, not all new listings.
- The hypothesis here is again, one of zero-knowledge.
- This means the tool does not require you to know how your specified product should be priced; for example, you are not expected to know that a new iPhone 18 Pro Max retails for around £1200 - the tool will infer this automatically.  
    - Note that, while not recommended, manual price filters are possible, see [here](#setting-up-filters).
- "Good deals" are identified by calculating statistics from either one of two sources: 
    1. Your own data.
    1. The local database of active listings.
- In general, the tool checks for user data before using the local database of active listings for statistics.

#### User Data Method
- This method can be very useful, because it allows conclusions to be drawn from sold listings, which are not available via eBay's public API.
- The tool can use data extracted from user-provided HTML pages from the eBay site. 
- The filters are largely similar across the API and the eBay website, so the tool can generate a URL for a given filter, and open this URL in your browser. 
- From there, you simply install the HTML source of the page, and upload it to the parser tool (see [here](#handy-scripts)), and it will extract all listings and upload them to a local database.

#### Active Listing Method
- This method is convenient, because it does not require any work on your behalf, but it can present a few issues:
    1. Active listings at a given moment may not be representative of the intrinsic price of a product, for example if the only listings left active are unwanted for price or condition reasons.
    2. There may not *be* any active listings for a completely valid filter, especially if it is for a product at a price that is in very high demand.
- The former issue can be mitigated somewhat by building up a database of formerly active listings, thus creating a more representative sample to draw statistical conlusions from. This means that having the tool running for a longer period of time increases its usability.
- The latter is a more difficult problem, especially because "building up a database" now means missing out on potential deals. To this end, the tool will have a setting to notify on **all** new listings, thereby ensuring there are no missed opportunities for very strict filters. (See [here](#configuring-alerts)).

### Alerts
- Work in progress. Many features missing or incomplete.
- Alerts are generated whenever some condition is met. 
- As of right now, only a Discord bot is planned.

## Handy Scripts
- Work in Progress. Will be updated soon.
**HTML to CSV converter**
- Usage: `html2csv path/to/html/file item_name`
- See `scripts/html2csv.py` for more details

## Disclaimers
- This tool automatically retrieves listings using eBay's official API **only**. Scraping listings from the eBay site is strictly against eBay's Terms of Service.
- This tool **does not** automatically purchase listings. This is also against eBay's Terms of Service.

[1]: https://docs.astral.sh/uv/getting-started/installation/
[2]: https://docs.discord.com/developers/quick-start/getting-started
[3]: https://developer.ebay.com/my/keys
