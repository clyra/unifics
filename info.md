{% if installed %}
## Changes as compared to your installed version:

### Breaking Changes

### Changes

### Features

{% if version_installed.replace("v", "").replace(".","") | int < 141  %}
- Added `mode: bicycle`
- Added `mode: publicTransportTimeTable` - Please look [here](https://developer.here.com/documentation/routing/topics/public-transport-routing.html) for differences between the two public modes.
{% endif %}
{% if version_installed.replace("v", "").replace(".","") | int < 142  %}
- Release notes are shown in HACS depending on your installed version
{% endif %}

### Bugfixes

{% if version_installed.replace("v", "").replace(".","") | int < 143  %}
- Fix for `mode: publicTransportTimeTable` returning `No timetable route found`
{% endif %}
---
{% endif %}
