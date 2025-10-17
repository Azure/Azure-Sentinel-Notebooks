# Retroactive Hunting

### Overview

This notebook correlates Threat Intelligence Indicators, from the ThreatIntelIndicators table, with log data from multiple sources over a configurable lookback period, aggregates matches by TI indicator, and saves results to a managed table for further analysis.  Future runs will reference matches already in the result set to avoid generating duplicate alerts each time this notebook is run.

### How to Run Notebook

Reference the general [Sentinel Notebook Readme](../README.md) for guidance on installing and running notebooks.  

For this job specifically there is job yaml file included.  Action required by users on that job yaml:
- **StartTime**: What day and time the job should start running.
- **EndTime**: What day and time the job should stop running.
- **JobName(Optional)**: If you decide to change the jobname, prefix the name with 'TI-Retroactive-Hunting'. 

### Key Features:
- **Multiple log source support**
- **Flexible matching modes**: current (TI valid now), loose (ignore validity)
- **Configurable log sources**: Enable/disable different log types as needed.
- **Adjustable lookback period**: Configure how long back it should look for matches.

### Currently Supported Log Sources:
- **SigninLogs**: Standard user sign-in activities.  This includes the following tables: SigninLogs, AADNonInteractiveUserSignInLogs, AADServicePrincipalSignInLogs, AADManagedIdentitySignInLogs.
- **Syslogs**: General table for logging system and security events.
- **CommonSecurityLogs**: Table for collecting events in the Common Event format from different security sources.

### Required Customer Input:
- **WORKSPACE_NAME**: Customer Log Analytics workspace name.  This will be used for retrieving indicator and log data, as well as for outputing match results.  If None is provided then the notebook will look for the first log analytics workspace that is not the Sentinel generated "System tables" workspace.  This is a string variable and must be wrapped in quotes.
- **LOOKBACK_DAYS**: 14-365.  Lookback time period for logs matching.  Default 30.
- **MATCH_MODE**: Which ThreatIntelIndicators to match against which logs: current (TI valid now), loose (ignore validity).  Default "current".
- Enabled the log sources that you would like to match against under the `LOG SOURCE TOGGLES - SUPPORTED` section.

### Output Schema:
Results are aggregated by TI indicator with match counts and event references for detailed analysis.  The RetroThreatMatchResults_SPRK_CL output table will be generated on the provided Log Analytics workspace.

| Column Name | Type |Description |
|-------------|------|------------|
|MatchId | string |  Unique identifier for the match result record (reference to the original ThreatIntelIndicators Id) | 
|JobId | string | Identifier for the retroactive matching job execution.  This is a random uuid created by the notebook. |
| JobStartTime          | datetime         | Timestamp when the retro-matching job started. |
| JobEndTime            | datetime         | Timestamp when the retro-matching job completed. |
| MatchType             | string           | Type of match (e.g., "IoC", "Observable", "CVE", "TTP"/"MITRE-Technique"). |
| ObservableType        | string           | Subtype of the match (e.g., "IP", "Domain", "URL", "SHA256", "x509", "JA3").| 
| ObservableValue       | string           | Observable value (IoC value == Observable value).  Domain, IP, URL, etc. |
| TIReferenceId         | string           | Reference to the Threat Intelligence record (e.g., internal IoC ID or STIX ID). |
| TIValue               | string           | Actual IoC or observable value that was matched (e.g., "malicious.com", name of TTP, etc.). |
| MatchCount            | int              | Number of events or records in the environment that matched this TI object. |
| EventReferences       | dynamic          | Array of matched events with format `[{"Table":"Syslog","TimeGenerated":"2025-09-12T18:01:08.768Z","LogField":"SyslogMessage"},...]`. |
| TTPs                  | dynamic          | Array of MITRE techniques (e.g., `["T1059", "T1071.001"]`) associated with the matched TI. |
| ThreatActors          | dynamic          | Array of threat actor names tied to the matched TI object. |
| EnrichmentContext     | dynamic          | Optional dictionary of enrichment tags (e.g., industry, country, malware family, confidence score). |
| TenantId              | string           | Identifier of the customer environment (multi-tenant scenarios). |
| TimeGenerated | datetime | Timestamp of record creation in this table. |