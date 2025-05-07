# Changelog

All notable changes to this project will be documented in this file.  
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/).

[//]: # (## [Unreleased])

[//]: # (### Added)

[//]: # (- Description of any new feature or functionality added to the project.)

[//]: # ()
[//]: # (### Changed)

[//]: # (- Description of changes or improvements made to existing features.)

[//]: # ()
[//]: # (### Fixed)

[//]: # (- Description of bugs or issues that have been fixed.)

[//]: # ()
[//]: # (### Deprecated)

[//]: # (- Description of features that are no longer recommended for use and may be removed in future versions.)

[//]: # ()
[//]: # (### Removed)

[//]: # (- Description of any features that were removed from the project.)

[//]: # ()
[//]: # (### Security)

[//]: # (- Description of any security issues that were addressed.)
---

## [1.2.0] 2025-05-06
### Added
- Revert changes made on Botasaurus driver: go back to Playwright.

---

## [1.1.0] 2025-03-27
### Added
- Try using Botasaurus browser instead of Playwright for ad downloading. (Cf [Repo Botasaurus](https://github.com/omkarcloud/botasaurus/tree/70a67abcead7b39cba32e947240d30aaafa704b2))

---

## [1.0.18] 2025-03-18
### Added
- Avoid getting flagged by Ad Libraries when downloading ads by slowing the extraction process.

---

## [1.0.17] 2025-03-11
### Added
- Improvement to 1.0.15 modifications: clean open Playwright pages.

---

## [1.0.16] 2025-03-11
### Added
- Add the opportunity to provide a proxy to run playwright with

---

## [1.0.15] 2025-03-10
### Added
- Try downloading ad elements from a public Meta link first ("https://www.facebook.com/ads/library/?id=***")
- Use the Meta render_ad preview (private access using access_token) only if it can't be done using public url

---

## [1.0.14] 2025-03-07
### Added
- Detect when Meta is blocking Playwright and store the info in ad_elements payload

---

## [1.0.12 to 1.0.13] 2025-03-06
### Added
- Add new scraping elements:
  - for images without bottom section (title + CTA), the locators are different
  - videos location may vary: use "//video" to detect any video child section 

---

## [1.0.8 to 1.0.11] 2025-03-03 to 2025-03-05
### Added
- Clean Playwright use to avoid having process killed with errors (cf Issue)[https://github.com/Spark-Data-Team/nanga-ad-library/issues/17]
- Try to block Meta redirections to Login pages
- Pass randomly picked User-Agent to Playwright context (class "UserAgent" + file "user_agents.txt" in utils)

---

## [1.0.7] 2025-02-25
### Added
- Use delivery_start_date to check if the ad has to be downloaded

---

## [1.0.5 to 1.0.6] 2025-01-27
### Added
- Add download date_range:
  ad elements will be scraped only if ad creation_date is between download_start_date and download_end_date.
- Refactor landing page url:
  extract main url from Meta embedded url and remove url tags/utms.
- Check that the scraping worked:
  ad elements type should not be 'status' if images or videos are intercepted.

---

## [1.0.4] 2025-01-16
### Added
- Remove playwright browsers auto-install

---

## [1.0.1 to 1.0.3] 2025-01-10
### Added
- Small repo setups [1.0.1]
- Fix issue template folder and files [1.0.2]
- Use find_packages in setup.py (for PyPI) [1.0.3]
- Use relative paths in init files [1.0.3]

---

## [1.0.0] 2024-11-11
### Added
- Initial release of the project with basic functionality and structure.

---

## [0.0.1] - 2024-10-24
### Added
- Initial development of the project.
