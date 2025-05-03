## v0.1.17 (2025-05-02)

### Feat

- provide twit author to the agent  (#1129)
- add message attachments to docs (#1128)
- add agent examples page (#1120)
- enhance framework deps information for docs (#1075)
- add list of supported packages (#1072)
- add issue templates for bugs, docs, & feature requests (#758)
- reworked `add_user_usage`:
- Added JSON parsing with error handling
- Uses SQLAlchemy session instead of direct DB connection
- Implements type conversion for query/response
- Added token usage data extraction
- DB Migration
- Adds token tracking columns (completion_tokens, prompt_tokens, etc.)
- Batch-updates existing records (1000/batch) with extracted usage data
- Recreates table with NOT NULL constraints, indexes, and SingleStore optimizations, utfmb4 support
- Uses AGGREGATOR SYNC AUTO_INCREMENT for distributed consistency
- Data Structure Changes
- Added token tracking fields to persistence layer
- Structured JSON storage instead of raw string storage
- restrict messages to thread owner (#1036)
- upgrade openai dependency to 1.66.2 (#1022)

### Fix

- correctly convert input `content` (#1117)
- update python sdk link (#1105)
- add local=true when running interactive from list (#1104)
- promote meteor wallet as recommended way to create a free account (#1103)
- Handle Redirects in async_fetch_json (#1056)
- update cli install instructions (#1065)
- update info block formatting error (#1062)
- The key fix was changing response to response_dict in the usage check. This ensures parsed JSON data is used. (#1057)
- Security Improvements
- Removed string interpolation in SQL queries
- Uses parameterized ORM operations to prevent injections
- release action commit with uv sync (#1025)

## v0.1.15 (2025-03-12)

### Fix

- move rich display logic to cli_helpers.py (#1013)

## v0.1.14 (2025-03-11)

### Feat

- add auto versioning (#973)
- Forking agents now removes X (Twitter) event triggers to prevent scheduler extra run. Ensures forked agents start clean, requiring users to configure their own X integrations. (#988)
- add objects as options for combobox in request_data country-name (#968)
- image-to-image support for fireworks.ai (#984)
- setup_and_run.sh to back up old log files before starting new processes (#974)
- enhance agent create next steps (#970)
- add agent embed docs (#965)
- cached agent creation from constructor added (#938)
- env.find_agents to get offset & limit args (#945)
- add MIT License (#943)
- add docs agent tutorial (#901)
- web agent to support eth libs
- ts runner to support vector stores (#913)

### Fix

- add all folders in the root directory as potential modules to import (#960)
- move docs agent to tutorial section (#950)

## v0.1.13 (2025-02-21)

### Feat

- enhance readme (#856)
- `latest_versions_only` argument added to `env.find_agents` (#914)
- add `mkdocs-redirect` plugin (#917)
- enhance alpha section with CTAs (#874)
- enhance secrets & env variables (#879)
- frameworks base/web-agent -> minimal/standard (#892)
- multiple workers support (#886)
- web agent to support eth libs (#887)

### Fix

- minor typos in `private-ml-sdk.md` (#873)
- readme path fixed for py_runner (#897)

## v0.1.12 (2025-02-19)

### Feat

- add optional docs deps in toml (#877)
- add docs PR preview (#888)
- add mcp dependency to base framework requirements (#864)
- sql method to `list_vector_store_files` (#859)
- local runner to support multiple agents in parallel. Doc: aws_t… (#854)
- debug mode to return python error & python traceback (#833)

### Fix

- callback_url cannot be None, replace default value to "" to auto-generated signature (#880)
- signer_account_id getter simplified (#881)
- do not try to cloudwatch value if value is null (#883)
- update registry doc (#878)
- recreate agent files in `temp_dir` for both py and ts cached agents (#868)
- Proper unicode handling in JSON content using UnicodeSafeJSON (#834)
- Introduced `UnicodeSafeJSON` type decorator using LONGTEXT storage
fix: Updated Message model's content field
fix: Singlestore connection string updated to force charset

## v0.1.11 (2025-02-11)

### Feat

- Ensure the user is authenticated on agent local run (#822)

### Fix

- Removed unnecessary retries in HUB (#827)

## v0.1.10 (2025-02-01)

### Feat

- update agent quickstart guide (#782)

## v0.1.9 (2025-01-31)

## v0.1.8 (2025-01-31)

[main 302d4110] bump: version 0.1.16 → 0.1.17
 2 files changed, 132 insertions(+), 1 deletion(-)

