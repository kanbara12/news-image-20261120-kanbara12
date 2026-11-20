# The World in One Day — Friday 20 November 2026

[![make.fun](https://make.fun/bounty/news-image-20261120/badge.svg)](https://make.fun/bounty/news-image-20261120)
[![make.fun — news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120)

A single dense newspaper front page for Friday 20 November 2026. It carries forty stories from seven regions: three large illustrated leads, ten more illustrated briefs, and twenty-seven one-line also-on items, plus a world map with numbered pins for the illustrated stories, a strip of six big numbers, a timeline of the day, and a DATE CHECK box naming the earlier news that was left out on purpose.

## How the page is drawn

`render.py` paints entry.png at 1024 by 1024. The thirteen pictures come from three painterly editorial strips drawn for this entry (under assets/), one per illustrated story, each cropped into its panel with a caption bar naming the place. `main.py` runs the renderer and moves the finished PNG into the harness output directory. The program uses only the Python standard library and Pillow, makes no network requests, and writes the same bytes on every run.

## What is inside

- The three leads: COP31's fossil-free draft on its final day in Antalya, Cyclone Akvan making landfall on India's east coast, and the AI selloff dragging Wall Street below 50,000.
- Ten illustrated briefs: the morning after the Shenzhen summit, Kyiv hit by four ballistic missiles, Britain pledging 1,000 drones for Ukraine, the Houthi attack on Riyadh's PIF tower, a tanker ablaze off Hormuz, Israel's raid beyond the Gaza ceasefire line, Europe ready for Russia talks, Poland probing mystery objects, Czech leaders visiting Israel, and Tiger Woods designing a golf course in Northern Ireland.
- The also-on list and the map carry the remaining twenty-seven stories, from the third Crimean Bridge strike and the Taiwan stock plunge to the Senegal boat capsizing and the US sanctions on the Comancheros and the 'Ndrangheta.

This page was built after studying the competition's live top five, and it follows the formula they share: a front page, a story count, seven regions, a KPI strip, a world map, and a strict DATE CHECK. A Hydrogen review of the first plan caught the Shenzhen summit presented as Friday news when it happened on Thursday, so COP31 leads instead and Shenzhen is one brief about the morning after. Stories first reported on Thursday 19 November — the ICJ ruling that Myanmar committed genocide against the Rohingya, the Shenzhen summit itself, Anthropic's Nasdaq debut, the US Senate's 51–48 rejection of the Iran war-powers resolution — are named in DATE CHECK as excluded, not presented as Friday news.

Every story here happened, or was first reported, on Friday 20 November 2026. Disputed claims are attributed, not stated as fact. Sources: Reuters, BBC, WSJ, AP, IMD, CNN. Original illustrations.

---

Built for the make.fun news-image-20261120 competition. If you want to try make.fun yourself, this is my referral link: https://make.fun/?ref=wfzk99wk
