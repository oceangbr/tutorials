# Beaufort12 Support Site Audit Report

- Started at (UTC): **2026-02-24T22:59:50Z**
- Support pages audited: **95**
- Pages fetched successfully (HTTP 200): **95**

## Summary (links)

- Unique anchor links checked: **738**
- Broken internal links: **5**
- Internal links with missing `#fragment` targets: **5**
- Internal links redirecting http→https (inconsistency): **10**
- Broken external links (HTTP 4xx/5xx): **5**
- External links with TLS/SSL verification failures: **4**
- External links blocked/unverifiable automatically: **3**

## Broken internal links (beaufort12.com)

### https://www.beaufort12.com/emma/support/import-wizard.

- Status: **404**
- Error: `HTTP 404`

Source pages:
- https://www.beaufort12.com/emma/support/emma-segments (trailing-punct='.') — “import wizard.”
- https://www.beaufort12.com/emma/support/import-wizard (trailing-punct='.') — “import wizard.”

### https://www.beaufort12.com/mailchimp/support)

- Status: **404**
- Error: `HTTP 404`

Source pages:
- https://www.beaufort12.com/mailchimp/support/setup-guide (trailing-punct=')') — “https://www.beaufort12.com/mailchimp/support)”
- https://www.beaufort12.com/scoring/support/setup-guide (trailing-punct=')') — “https://www.beaufort12.com/mailchimp/support)”

### https://www.beaufort12.com/mc4faqs/can-i-map-to-a-mailchimp-sms-field

- Status: **404**
- Error: `HTTP 404`

Source pages:
- https://www.beaufort12.com/mailchimp/support/field-mappings — “Mailchimp SMS”

### https://www.beaufort12.com/mc4faqs/manage-data-storage-for-email-activity

- Status: **404**
- Error: `HTTP 404`

Source pages:
- https://www.beaufort12.com/mailchimp/support/getting-started — “How do I manage data storage for email activity?”
- https://www.beaufort12.com/scoring/support/getting-started — “How do I manage data storage for email activity?”

### https://www.beaufort12.com/mc4faqs/whats-causing-missing-email-activity-data-for-ab-split-test-campaigns

- Status: **404**
- Error: `HTTP 404`

Source pages:
- https://www.beaufort12.com/mailchimp/support/getting-started — “What's causing the missing email-activity data for A/B (split-test) campaigns?”
- https://www.beaufort12.com/scoring/support/getting-started — “What's causing the missing email-activity data for A/B (split-test) campaigns?”

## Internal links with missing fragment targets

- `http://www.beaufort12.com/campaignmonitor-faq/how-can-i-change-the-sync-user-cm#reconnect` (fragment `#reconnect` not found on `https://www.beaufort12.com/campaignmonitor-faq/how-can-i-change-the-sync-user-cm`)
  Source pages:
  - https://www.beaufort12.com/campaignmonitor/support/manage-general-settings — “How can I change the sync user in Campaign Monitor?”
- `https://www.beaufort12.com/campaignmonitor/support/import-wizard#segments` (fragment `#segments` not found on `https://www.beaufort12.com/campaignmonitor/support/import-wizard`)
  Source pages:
  - https://www.beaufort12.com/campaignmonitor/support/release-notes — “click here”
- `https://www.beaufort12.com/campaignmonitor/support/manage-billing#Billing` (fragment `#Billing` not found on `https://www.beaufort12.com/campaignmonitor/support/manage-billing`)
  Source pages:
  - https://www.beaufort12.com/campaignmonitor/support/manage-billing — “click here”
- `https://www.beaufort12.com/campaignmonitor/support/manage-billing#ChangePlan` (fragment `#ChangePlan` not found on `https://www.beaufort12.com/campaignmonitor/support/manage-billing`)
  Source pages:
  - https://www.beaufort12.com/campaignmonitor/support/manage-billing — “support article”
- `https://www.beaufort12.com/mailchimp/support/technical-guide#sts=Sandboxes` (fragment `#sts=Sandboxes` not found on `https://www.beaufort12.com/mailchimp/support/technical-guide`)
  Source pages:
  - https://www.beaufort12.com/mailchimp/support/maintenance — “Sandbox Guide”
  - https://www.beaufort12.com/scoring/support/maintenance — “Sandbox Guide”

## Broken external links (HTTP 4xx/5xx)

- `https://jmp.sh/cqdKt6sy)` → **404**
  Source pages:
  - https://www.beaufort12.com/emma/support/emma-segments (trailing-punct=')') — “https://jmp.sh/cqdKt6sy)”
  - https://www.beaufort12.com/emma/support/import-wizard (trailing-punct=')') — “https://jmp.sh/cqdKt6sy)”
- `https://jmp.sh/tQhzXuAo)` → **404**
  Source pages:
  - https://www.beaufort12.com/mailchimp/support/activity-history (trailing-punct=')') — “https://jmp.sh/tQhzXuAo)”
- `https://trailhead.salesforce.com/en/content/learn/modules/reports_dashboards/reports_dashboards_overview` → **404**
  Source pages:
  - https://www.beaufort12.com/campaignmonitor/support/reports-and-dashboards — “Salesforce Trailhead”
  - https://www.beaufort12.com/emma/support/getting-started — “Salesforce Trailhead”
  - https://www.beaufort12.com/eventbrite/support/billing — “Salesforce training course”
  - _(and 9 more source page(s))_
- `https://trailhead.salesforce.com/en/users/rrajput24/trailmixes/web-to-lead-in-salesforce` → **404**
  Source pages:
  - https://www.beaufort12.com/campaignmonitor/support/subscriber-rules — “click here”
- `https://trailhead.salesforce.com/live/videos/a2r3k000001n21B/reports-and-dashboards---custom-report-types/?lang=en` → **404**
  Source pages:
  - https://www.beaufort12.com/eventbrite/support/billing — “Salesforce trailhead.”
  - https://www.beaufort12.com/eventbrite/support/eventbrite-for-salesforce — “Salesforce trailhead.”
  - https://www.beaufort12.com/eventbrite/support/installation-setup — “Salesforce trailhead.”
  - _(and 7 more source page(s))_

## External links with TLS/SSL verification failures

_These could be real certificate/chain issues or an environment CA-chain limitation; verify in a normal browser._

- `https://help.myemma.com/s/` → **TLS/SSL verification failed**
  - Error: `SSLError: HTTPSConnectionPool(host='help.myemma.com', port=443): Max retries exceeded with url: /s/ (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1000)')))`
  Source pages:
  - https://www.beaufort12.com/emma/support/technical-guide — “https://help.myemma.com/s/”
- `https://help.myemma.com/s/article/How-to-use-merge-tags-for-personalization#PURL` → **TLS/SSL verification failed**
  - Error: `SSLError: HTTPSConnectionPool(host='help.myemma.com', port=443): Max retries exceeded with url: /s/article/How-to-use-merge-tags-for-personalization (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1000)')))`
  Source pages:
  - https://www.beaufort12.com/emma/support/emma-segments — “Emma's Personalized URL”
  - https://www.beaufort12.com/emma/support/import-wizard — “Emma's Personalized URL”
- `https://help.myemma.com/s/article/Our-open-API` → **TLS/SSL verification failed**
  - Error: `SSLError: HTTPSConnectionPool(host='help.myemma.com', port=443): Max retries exceeded with url: /s/article/Our-open-API (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1000)')))`
  Source pages:
  - https://www.beaufort12.com/emma/support/installation-setup — “How to generate your API keys”
  - https://www.beaufort12.com/emma/support/manage-general-settings — “support guide”
- `https://support.e2ma.net/s/article/Trigger-events-contact-import` → **TLS/SSL verification failed**
  - Error: `SSLError: HTTPSConnectionPool(host='support.e2ma.net', port=443): Max retries exceeded with url: /s/article/Trigger-events-contact-import (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1000)')))`
  Source pages:
  - https://www.beaufort12.com/emma/support/manage-billing — “https://support.e2ma.net/s/article/Trigger-events-contact-import”
  - https://www.beaufort12.com/emma/support/permissions — “https://support.e2ma.net/s/article/Trigger-events-contact-import”
  - https://www.beaufort12.com/emma/support/sign-up-form-using-salesforce-web-to-lead — “https://support.e2ma.net/s/article/Trigger-events-contact-import”

## External links blocked / unverifiable automatically

_These returned 403/429/999 (bot protection/rate limiting). They may still work for human users._

- `https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_campaignmemberstatus.htm` → **403**
  Source pages:
  - https://www.beaufort12.com/campaignmonitor/support/salesforce-campaigns — “https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_campaignmemberstatus.htm”
- `https://developer.salesforce.com/docs/atlas.en-us.packagingGuide.meta/packagingGuide/security_review_create_secure_solution.htm` → **403**
  Source pages:
  - https://www.beaufort12.com/mailchimp/support/setup-guide — “Salesforce Security Review”
  - https://www.beaufort12.com/scoring/support/setup-guide — “Salesforce Security Review”
- `https://www.linkedin.com/in/gardengnome/` → **999**
  Source pages:
  - https://www.beaufort12.com/emma/support/manage-billing — “Barbara’s LinkedIn”
  - https://www.beaufort12.com/emma/support/permissions — “Barbara’s LinkedIn”
  - https://www.beaufort12.com/emma/support/sign-up-form-using-salesforce-web-to-lead — “Barbara’s LinkedIn”

## Internal http→https redirect inconsistencies (non-breaking)

- `http://beaufort12.com/campaignmonitor/support/subscriber-rules` → `https://www.beaufort12.com/campaignmonitor/support/subscriber-rules`
- `http://www.beaufort12.com/campaignmonitor-faq/how-can-i-change-the-sync-user-cm` → `https://www.beaufort12.com/campaignmonitor-faq/how-can-i-change-the-sync-user-cm`
- `http://www.beaufort12.com/campaignmonitor-faq/insufficient-permissions-secure-query-included-inaccessible-field` → `https://www.beaufort12.com/campaignmonitor-faq/insufficient-permissions-secure-query-included-inaccessible-field`
- `http://www.beaufort12.com/mc4faqs/how-can-i-segment-my-salesforce-data-in-mailchimp` → `https://www.beaufort12.com/mc4faqs/how-can-i-segment-my-salesforce-data-in-mailchimp`
- `http://www.beaufort12.com/mc4faqs/how-can-preview-mapping-rules` → `https://www.beaufort12.com/mc4faqs/how-can-preview-mapping-rules`
- `http://www.beaufort12.com/mc4faqs/how-do-i-add-a-merge-field-to-mailchimp` → `https://www.beaufort12.com/mc4faqs/how-do-i-add-a-merge-field-to-mailchimp`
- `http://www.beaufort12.com/mc4faqs/how-do-i-connect-to-a-custom-domain` → `https://www.beaufort12.com/mc4faqs/how-do-i-connect-to-a-custom-domain`
- `http://www.beaufort12.com/mc4faqs/how-do-i-segre` → `https://www.beaufort12.com/mc4faqs/how-do-i-segre`
- `http://www.beaufort12.com/mc4faqs/how-does-matching-work` → `https://www.beaufort12.com/mc4faqs/how-does-matching-work`
- `http://www.beaufort12.com/mc4faqs/what-happens-when-i-first-connect-my-mailchimp-account-in-mailchimp-settings` → `https://www.beaufort12.com/mc4faqs/what-happens-when-i-first-connect-my-mailchimp-account-in-mailchimp-settings`

## Potential text inconsistencies / typos (rule-based)

- **premuim_typo** on https://www.beaufort12.com/campaignmonitor/support/2022-pricing-changes
  - Match: `premuim`
  - Suggestion: Typo: “premuim” → “premium”.
  - Snippet: “e please see this article . What features are included? The premuim plan features can be found by clicking here . If you need t”
- **space_before_punct** on https://www.beaufort12.com/campaignmonitor/support/2022-pricing-changes
  - Match: `article .`
  - Suggestion: Remove the extra space before punctuation.
  - Snippet: “e automatically moved if you need to update please see this article . What features are included? The premuim plan features can b”
- **space_before_punct** on https://www.beaufort12.com/campaignmonitor/support/2022-pricing-changes
  - Match: `here .`
  - Suggestion: Remove the extra space before punctuation.
  - Snippet: “ncluded? The premuim plan features can be found by clicking here . If you need to upgrade to Enterprise please contact us. Wha”
- **space_before_punct** on https://www.beaufort12.com/campaignmonitor/support/2022-pricing-changes
  - Match: `page .`
  - Suggestion: Remove the extra space before punctuation.
  - Snippet: “rprise plans to learn more please see the dedicated pricing page . How do I move tiers? This process is automated and based on”
- **space_before_punct** on https://www.beaufort12.com/campaignmonitor/support/2022-pricing-changes
  - Match: `us .`
  - Suggestion: Remove the extra space before punctuation.
  - Snippet: “e. How do I cancel? You can cancel at anytime by contacting us . What currency do you charge in? All pricing is in US dollar”
- **duplicate_word** on https://www.beaufort12.com/campaignmonitor/support/creating-salesforce-records
  - Match: `the the`
  - Suggestion: Remove duplicated word (e.g., “the the”).
  - Snippet: “nk at the bottom of the member details screen to check that the the subscriber is not Suppressed . ‍ A record is not being crea”
- **space_before_punct** on https://www.beaufort12.com/campaignmonitor/support/creating-salesforce-records
  - Match: `Save .`
  - Suggestion: Remove the extra space before punctuation.
  - Snippet: “tion dropdown and choose to create contacts or leads. Click Save . Default values On the same page, you can assign default val”
- **space_before_punct** on https://www.beaufort12.com/campaignmonitor/support/creating-salesforce-records
  - Match: `mappings .`
  - Suggestion: Remove the extra space before punctuation.
  - Snippet: “les configured in both the Create records section and Field mappings . If there is an error attempting to refresh the subscriber,”
- **space_before_punct** on https://www.beaufort12.com/campaignmonitor/support/creating-salesforce-records
  - Match: `Suppressed .`
  - Suggestion: Remove the extra space before punctuation.
  - Snippet: “mber details screen to check that the the subscriber is not Suppressed . ‍ A record is not being created in Salesforce how can I tro”
- **space_before_punct** on https://www.beaufort12.com/campaignmonitor/support/email-opt-out
  - Match: `list .`
  - Suggestion: Remove the extra space before punctuation.
  - Snippet: “Remove subscribers from all lists or Only remove from this list . The recommended setting is to remove from all lists. This e”
- **space_before_punct** on https://www.beaufort12.com/campaignmonitor/support/email-opt-out
  - Match: `here .`
  - Suggestion: Remove the extra space before punctuation.
  - Snippet: “turn if on via our general settings tab to learn more click here . When this option is enabled a Salesforce user (with one of”
- **space_before_punct** on https://www.beaufort12.com/campaignmonitor/support/email-opt-out
  - Match: `here .`
  - Suggestion: Remove the extra space before punctuation.
  - Snippet: “turn if on via our general settings tab to learn more click here . When this option is enabled and when a Salesforce contact o”
- **segement_typo** on https://www.beaufort12.com/campaignmonitor/support/import-wizard
  - Match: `segement`
  - Suggestion: Typo: “segement” → “segment”.
  - Snippet: “Wizard Segments This option needs to be enabled to show the segement option as part of the import wizard see above. Scheduling S”
- **duplicate_word** on https://www.beaufort12.com/campaignmonitor/support/release-notes
  - Match: `to to`
  - Suggestion: Remove duplicated word (e.g., “the the”).
  - Snippet: “list values now use Salesforce labels When a value is added to to Campaign Monitor we use the Salesforce label rather than th”
- **duplicate_word** on https://www.beaufort12.com/campaignmonitor/support/troubleshooting
  - Match: `the the`
  - Suggestion: Remove duplicated word (e.g., “the the”).
  - Snippet: “nk at the bottom of the member details screen to check that the the subscriber is not Suppressed . Troubleshooting email opt ou”
- **duplicate_word** on https://www.beaufort12.com/eventbrite/support/maintenance-codes-messages
  - Match: `the the`
  - Suggestion: Remove duplicated word (e.g., “the the”).
  - Snippet: “ULE An error occurred when trying to setup the schedule for the the primary sync. The most likely cause is that you have too ma”
- **duplicate_word** on https://www.beaufort12.com/eventbrite/support/mappings
  - Match: `the the`
  - Suggestion: Remove duplicated word (e.g., “the the”).
  - Snippet: “s to Salesforce records. By default the match is made using the the standard Salesforce email address field. For many customers”
- **duplicate_word** on https://www.beaufort12.com/eventbrite/support/release-notes
  - Match: `a a`
  - Suggestion: Remove duplicated word (e.g., “the the”).
  - Snippet: “nt date filter on storage screen Previously you had to open a a separate filter screen to change the event date filter. To”
- **duplicate_word** on https://www.beaufort12.com/mailchimp/support/audiences
  - Match: `to to`
  - Suggestion: Remove duplicated word (e.g., “the the”).
  - Snippet: “n use, it must be mapped in field mappings toward Mailchimp to to ensure that changes are reflected in both systems. In concl”
