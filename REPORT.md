# Ski Nav QA report

**Overall: 78 issue(s)**

## engine

Tour finished: yes · checks 21/21 passed · layout issues 0 · JS/app errors 0 · screenshots 0

### Behaviour checks

- PASS native engine matches web: Avoriaz day 1: swift 33.49 km, max 53.6 km/h, vert 5173 m vs web 33.49 km
- PASS native engine matches web: NYC practice: swift 8.05 km, max 15.9 km/h, vert 42 m vs web 8.05 km
- PASS watch can read the phone's plan: plan-avoriaz.json: OK 38
- PASS watch can read the phone's plan: plan-nyc.json: OK 8
- PASS glance: short name 'Chaux Fleuries': Chaux Fleuries
- PASS glance: short name 'Ardent gondola': Ardent gondola
- PASS glance: short name 'Chaux Fleurie chair': Chaux Fleurie chair
- PASS glance: short name 'Proclou': Proclou
- PASS glance: skiing: 42 km/h Chaux Fleuries next Ardent gondola 1469 m
- PASS glance: planned lift: Ardent gondola 59% 2 min then Parchets
- PASS glance: unplanned lift: Lift '' 0
- PASS glance: no plan: 36 ''
- PASS glance: phone to watch round trip: 265 bytes
- PASS glance: face: trip morning: morning Châtel side | 24 km planned · first lift 9:15 | DAY 3
- PASS glance: face: skiing: 42 ON A RED 12.4 of 24 km Next: Ardent gondola · 1.2 km
- PASS glance: face: on a lift: 4 top in 4 min Then: Lindarets, blue
- PASS glance: face: live numbers go stale after 15 min: done
- PASS glance: face: day done: Folie Douce till 6 26.1 km Tomorrow: Day 4
- PASS glance: face: countdown: Avoriaz in 10 days
- PASS glance: face: yesterday's totals don't show the next morning: morning
- PASS glance: face: save round trip

### Layout per screen

| screen | page | targets | too small (<44) | glove (<52) | covered | offscreen | sideways scroll | tiny text (<12px) | crowded |
|---|---|---|---|---|---|---|---|---|---|

## ios-sim

Tour finished: yes · checks 43/43 passed · layout issues 26 · JS/app errors 0 · screenshots 31

### Behaviour checks

- PASS page loads and map is ready (index.html): 79 steps
- PASS gear opens settings
- PASS settings fit without scrolling: 763 vs 763
- PASS week fits without scrolling: 652 vs 652
- PASS Follow the plan toggle works (off by default): false -> true -> false
- PASS menu lists the days: 6 day buttons
- PASS tapping Day 2 switches the plan: Avoriaz -> Morzine + Les Gets
- PASS menu closes
- PASS live lift status loads from the internet: 7 of 182 open
- PASS guide button opens the morning brief: Morning! Day one. The mountain doesn't know what's coming. What are we doing tod
- PASS Today sheet opens
- PASS Ask answers a question: First up: Ski Proclou (green), planned for 9:00.Steps
- PASS steps sheet closes
- PASS next and previous step buttons: 0 -> 1 -> 0
- PASS Remaining filter chip toggles
- PASS Runs view returns to route
- PASS tracking shows the stats card
- PASS Sun mode switches on
- PASS trail of where you have been is recorded: 1235 trail points
- PASS free ski by default: no off-route banner: hidden
- PASS test replay moves the skier and counts km: km=9.92 max=53 step 0->11 pill="Test replay"
- PASS Plan from here builds a connected route: {"routed":0,"rejoin":11,"minutes":0} max gap 52 m
- PASS Plan from here explains what it did: You’re already on the plan. Next up: Take Prodains Express 3S gondola.
- PASS day recap shows the day: km=9.9 vert=156 top=53 lifts=4 goal=1 of 62 +1 today
- PASS home sheet is back after stopping: Avoriaz
- PASS stop & reset clears the replay: km=0.00
- PASS ME shows my location without tracking: blue dot on map
- PASS compass button responds: pressed=false (no compass on this device, turned itself off)
- PASS native GPS fixes arrive: 23 fixes, raw path 254 m, speeds none, acc 5 m, alt undefined
- PASS simulator route is moving (test harness): 23 fixes, raw path 254 m, speeds none, acc 5 m, alt undefined
- PASS moving GPS turns into km and speed: km=0.25 speed=27 max=35 pill="GPS ±5 m" vs raw path 254 m
- PASS following link: nyc.html
- PASS page loads and map is ready (nyc.html): 8 steps
- PASS Practice in NYC link opens the NYC map: nyc.html
- PASS NYC page has a working way back: index.html
- PASS lock screen and Dynamic Island views render: 90-glances.png
- PASS watch screen renders: now: 97-watch-now.png
- PASS watch screen renders: lift: 97-watch-lift.png
- PASS watch screen renders: steps: 97-watch-steps.png
- PASS watch screen renders: face-morning: 97-watch-face-morning.png
- PASS watch screen renders: face-skiing: 97-watch-face-skiing.png
- PASS watch screen renders: face-lift: 97-watch-face-lift.png
- PASS watch screen renders: face-done: 97-watch-face-done.png

### Layout per screen

| screen | page | targets | too small (<44) | glove (<52) | covered | offscreen | sideways scroll | tiny text (<12px) | crowded |
|---|---|---|---|---|---|---|---|---|---|
| main | index.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| menu | index.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| menu-settings | index.html | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| brief | index.html | 15 | 0 | 0 | 10 | 0 | 0 | 3 | 6 |
| today | index.html | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| ask | index.html | 19 | 6 | 0 | 10 | 0 | 0 | 0 | 6 |
| steps | index.html | 11 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| progress | index.html | 14 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| runs-list | index.html | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| places | index.html | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| map-3d | index.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| map-all | index.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| test-mode | index.html | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay | index.html | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay-sun | index.html | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| plan-from-here | index.html | 11 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| recap | index.html | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| me-button | index.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| gps-tracking | index.html | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| nyc-main | nyc.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| nyc-menu | nyc.html | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

#### brief
- Covered (tap goes elsewhere): {"el": "#menuBtn \"Week, places and settings\"", "by": "#bEyebrow \"SUN JAN 17 · MORNING BRIEF\""}; {"el": "#wxPill \"Today's brief: the day, weather, what to\"", "by": "#bEyebrow \"SUN JAN 17 · MORNING BRIEF\""}; {"el": "#followBtn \"ME\"", "by": "#bClose \"Close\""}; {"el": "#compassBtn \"Compass\"", "by": "div.gstage"}; {"el": "#fitBtn \"ALL\"", "by": "div.gstage"}; {"el": "#dimBtn \"3D\"", "by": "div.gstage"}; {"el": "#placesBtn \"Places on the map\"", "by": "#bCap \"Morning! Day one. The mountain doesn't k\""}; {"el": "#goBtn \"Start skiing\"", "by": "#bAsk \"Ask\""}; {"el": "#stepsBtn \"Steps\"", "by": "#bToday \"Weather and lifts in detail\""}; {"el": "#progBtn \"Runs\"", "by": "#bToday \"Weather and lifts in detail\""}
- Tiny text: {"el": "span \"24 lifts\"", "px": 11.52}; {"el": "span \"First move\"", "px": 11.52}; {"el": "span \"Partly cloudy\"", "px": 11.52}
- Crowded: {"a": "#followBtn \"ME\"", "b": "#bClose \"Close\"", "gap": -46}; {"a": "#goBtn \"Start skiing\"", "b": "#bPause \"Pause\"", "gap": -50}; {"a": "#goBtn \"Start skiing\"", "b": "#bAsk \"Ask\"", "gap": -50}; {"a": "#goBtn \"Start skiing\"", "b": "#bGo \"Start skiing\"", "gap": -50}; {"a": "#stepsBtn \"Steps\"", "b": "#bToday \"Weather and lifts in detail\"", "gap": -48}; {"a": "#progBtn \"Runs\"", "b": "#bToday \"Weather and lifts in detail\"", "gap": -48}

#### ask
- Too small: {"el": "button \"What’s next?\"", "w": 124, "h": 40}; {"el": "button \"Where’s lunch?\"", "w": 141, "h": 40}; {"el": "button \"Any lifts closed?\"", "w": 149, "h": 40}; {"el": "button \"Plan from here\"", "w": 136, "h": 40}; {"el": "button \"How much today?\"", "w": 159, "h": 40}; {"el": "button \"Call the group\"", "w": 131, "h": 40}
- Covered (tap goes elsewhere): {"el": "#menuBtn \"Week, places and settings\"", "by": "rect"}; {"el": "#wxPill \"Today's brief: the day, weather, what to\"", "by": "#aState \"Ask me anything about today\""}; {"el": "#followBtn \"ME\"", "by": "#aClose \"Close\""}; {"el": "#compassBtn \"Compass\"", "by": "div.abub.me \"What’s next?\""}; {"el": "#fitBtn \"ALL\"", "by": "#aConvo \"What’s next?First up: Ski Proclou (green\""}; {"el": "#dimBtn \"3D\"", "by": "#aConvo \"What’s next?First up: Ski Proclou (green\""}; {"el": "#placesBtn \"Places on the map\"", "by": "#aConvo \"What’s next?First up: Ski Proclou (green\""}; {"el": "#goBtn \"Start skiing\"", "by": "button \"Call the group\""}; {"el": "#stepsBtn \"Steps\"", "by": "#aHold \"Tap and talk\""}; {"el": "#progBtn \"Runs\"", "by": "#aHold \"Tap and talk\""}
- Crowded: {"a": "#followBtn \"ME\"", "b": "#aClose \"Close\"", "gap": -38}; {"a": "#goBtn \"Start skiing\"", "b": "button \"How much today?\"", "gap": -40}; {"a": "#goBtn \"Start skiing\"", "b": "button \"Call the group\"", "gap": -40}; {"a": "#goBtn \"Start skiing\"", "b": "#aHold \"Tap and talk\"", "gap": -12}; {"a": "#stepsBtn \"Steps\"", "b": "#aHold \"Tap and talk\"", "gap": -50}; {"a": "#progBtn \"Runs\"", "b": "#aHold \"Tap and talk\"", "gap": -50}

## web-group

Tour finished: yes · checks 53/53 passed · layout issues 0 · JS/app errors 0 · screenshots 19

### Behaviour checks

- PASS people button is in the menu
- PASS organizer creates the trip: AVZ-16D2
- PASS invite link shows the code: https://alonmaltzov.github.io/ski-nav/join.html?c=AVZ-16D2
- PASS copy puts the invite link on the clipboard: https://alonmaltzov.github.io/ski-nav/join.html?c=AVZ-16D2
- PASS organizer sees the group call setup
- PASS a bad WhatsApp link is refused
- PASS organizer saves the WhatsApp group link
- PASS a non-Splitwise link is refused
- PASS organizer saves the Splitwise link
- PASS join screen shows who invited you: Alon invited you to
- PASS Continue is off until a name is typed
- PASS friend joins the trip: ['Alon', 'Dana Levi']
- PASS friend gets "Talk with the group"
- PASS friend gets "Split costs"
- PASS friend can't change the WhatsApp link
- PASS join link is removed from the address bar: file:///home/runner/work/ski-nav/ski-nav/index.html
- PASS friend's phone sends its position while skiing (phone time 11:00)
- PASS a rough 48 m fix is still shared: 48
- PASS friend shows up on the other phone without a refresh
- PASS own dot is drawn in my group colour: rgb(124, 58, 237)
- PASS people button stays visible while tracking
- PASS friend appears on the organizer's map: 1
- PASS friends pill shows 1 friend: All 1
- PASS pill shows everyone by default: All 2
- PASS friend on a lift gets the lift badge
- PASS ALL shows a friend who is off the route
- PASS people pill opens "On your map"
- PASS Everyone mode hides the switches
- PASS switching someone off removes their dot
- PASS pill shows "1 of 2": 1 of 2
- PASS ALL leaves out people you hid
- PASS your choice is remembered on this phone: 1 of 2
- PASS tapping a name flies to them: {'lng': 6.775640000000067, 'lat': 46.20311000000001}
- PASS friend card opens
- PASS friend card has distance and ETA: 1.2 km / 18 min
- PASS Route to them ends at the friend: Dana Levi
- PASS meeting point shows on the friend's map
- PASS meeting point card opens: At 11:15 · set by Alon · 60 m from you
- PASS friend sees the organizer on the map
- PASS organizer's plan style is shared with the group: {'call': 'https://chat.whatsapp.com/TestGroupInvite123', 'split': 'https://www.splitwise.com/join/TestSplit123?v=s', 'variant': 'black'}
- PASS changing the plan style keeps the WhatsApp and Splitwise links: {'call': 'https://chat.whatsapp.com/TestGroupInvite123', 'split': 'https://www.splitwise.com/join/TestSplit123?v=s', 'variant': 'black'}
- PASS a friend can't change the plan
- PASS friend doesn't get Remove buttons
- PASS sharing off hides the friend from the map
- PASS organizer removes a member
- PASS removed friend leaves the group on their phone
- PASS a bad invite link says so: This invite link isn’t valid any more. Ask for a new one.
- PASS invite page on iPhone opens the app: skinav://join?c=AVZ-16D2
- PASS invite page on iPhone links to TestFlight: https://testflight.apple.com/join/kPyVvmk9
- PASS invite page (iphone) has no browser option (apps only)
- PASS invite page on Android opens the app (or downloads it): intent://join?c=AVZ-16D2#Intent;scheme=skinav;package=com.alonmaltzov.skinav;S.browser_fallback_url=https%3A%2F%2Fgithub
- PASS invite page on Android downloads the app when missing
- PASS invite page (android) has no browser option (apps only)

### Layout per screen

| screen | page | targets | too small (<44) | glove (<52) | covered | offscreen | sideways scroll | tiny text (<12px) | crowded |
|---|---|---|---|---|---|---|---|---|---|

## web-iphone16

Tour finished: yes · checks 30/30 passed · layout issues 26 · JS/app errors 0 · screenshots 19

### Behaviour checks

- PASS page loads and map is ready (index.html): 79 steps
- PASS gear opens settings
- PASS settings fit without scrolling: 728 vs 728
- PASS week fits without scrolling: 643 vs 643
- PASS Follow the plan toggle works (off by default): false -> true -> false
- PASS menu lists the days: 6 day buttons
- PASS tapping Day 2 switches the plan: Avoriaz -> Morzine + Les Gets
- PASS menu closes
- PASS live lift status loads from the internet: 7 of 182 open
- PASS guide button opens the morning brief: Morning! Day one. The mountain doesn't know what's coming. What are we doing tod
- PASS Today sheet opens
- PASS Ask answers a question: First up: Ski Proclou (green), planned for 9:00.Steps
- PASS steps sheet closes
- PASS next and previous step buttons: 0 -> 1 -> 0
- PASS Remaining filter chip toggles
- PASS Runs view returns to route
- PASS tracking shows the stats card
- PASS Sun mode switches on
- PASS trail of where you have been is recorded: 1272 trail points
- PASS free ski by default: no off-route banner: hidden
- PASS test replay moves the skier and counts km: km=9.80 max=52 step 0->11 pill="Test replay"
- PASS Plan from here builds a connected route: {"routed":1,"rejoin":12,"minutes":4} max gap 52 m
- PASS Plan from here explains what it did: New route from where you are: 1 step (about 4 min), then back on the plan at Crôt (blue) → Jean Vuarnet (red) → Crôt (bl
- PASS day recap shows the day: km=11.2 vert=161 top=52 lifts=5 goal=1 of 62 +1 today
- PASS home sheet is back after stopping: Avoriaz
- PASS stop & reset clears the replay: km=0.00
- PASS following link: nyc.html
- PASS page loads and map is ready (nyc.html): 8 steps
- PASS Practice in NYC link opens the NYC map: nyc.html
- PASS NYC page has a working way back: index.html

### Layout per screen

| screen | page | targets | too small (<44) | glove (<52) | covered | offscreen | sideways scroll | tiny text (<12px) | crowded |
|---|---|---|---|---|---|---|---|---|---|
| main | index.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| menu | index.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| menu-settings | index.html | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| brief | index.html | 15 | 0 | 0 | 10 | 0 | 0 | 3 | 6 |
| today | index.html | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| ask | index.html | 19 | 6 | 0 | 10 | 0 | 0 | 0 | 7 |
| steps | index.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| progress | index.html | 14 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| runs-list | index.html | 11 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| places | index.html | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| map-3d | index.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| map-all | index.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| test-mode | index.html | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay | index.html | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay-sun | index.html | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| plan-from-here | index.html | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| recap | index.html | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| nyc-main | nyc.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| nyc-menu | nyc.html | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

#### brief
- Covered (tap goes elsewhere): {"el": "#menuBtn \"Week, places and settings\"", "by": "#bEyebrow \"SUN JAN 17 · MORNING BRIEF\""}; {"el": "#wxPill \"Today's brief: the day, weather, what to\"", "by": "#bEyebrow \"SUN JAN 17 · MORNING BRIEF\""}; {"el": "#followBtn \"ME\"", "by": "#bClose \"Close\""}; {"el": "#compassBtn \"Compass\"", "by": "div.gstage"}; {"el": "#fitBtn \"ALL\"", "by": "div.gstage"}; {"el": "#dimBtn \"3D\"", "by": "div.gstage"}; {"el": "#placesBtn \"Places on the map\"", "by": "#bCap \"Morning! Day one. The mountain doesn't k\""}; {"el": "#goBtn \"Start skiing\"", "by": "#bAsk \"Ask\""}; {"el": "#stepsBtn \"Steps\"", "by": "#bToday \"Weather and lifts in detail\""}; {"el": "#progBtn \"Runs\"", "by": "#bToday \"Weather and lifts in detail\""}
- Tiny text: {"el": "span \"24 lifts\"", "px": 11.52}; {"el": "span \"First move\"", "px": 11.52}; {"el": "span \"Partly cloudy\"", "px": 11.52}
- Crowded: {"a": "#followBtn \"ME\"", "b": "#bClose \"Close\"", "gap": -46}; {"a": "#goBtn \"Start skiing\"", "b": "#bPause \"Pause\"", "gap": -50}; {"a": "#goBtn \"Start skiing\"", "b": "#bAsk \"Ask\"", "gap": -50}; {"a": "#goBtn \"Start skiing\"", "b": "#bGo \"Start skiing\"", "gap": -50}; {"a": "#stepsBtn \"Steps\"", "b": "#bToday \"Weather and lifts in detail\"", "gap": -48}; {"a": "#progBtn \"Runs\"", "b": "#bToday \"Weather and lifts in detail\"", "gap": -48}

#### ask
- Too small: {"el": "button \"What’s next?\"", "w": 142, "h": 40}; {"el": "button \"Where’s lunch?\"", "w": 161, "h": 40}; {"el": "button \"Any lifts closed?\"", "w": 170, "h": 40}; {"el": "button \"Plan from here\"", "w": 157, "h": 40}; {"el": "button \"How much today?\"", "w": 181, "h": 40}; {"el": "button \"Call the group\"", "w": 151, "h": 40}
- Covered (tap goes elsewhere): {"el": "#menuBtn \"Week, places and settings\"", "by": "rect"}; {"el": "#wxPill \"Today's brief: the day, weather, what to\"", "by": "span \"Ask me anything about todayWorks on your\""}; {"el": "#followBtn \"ME\"", "by": "#aClose \"Close\""}; {"el": "#compassBtn \"Compass\"", "by": "#aConvo \"What’s next?First up: Ski Proclou (green\""}; {"el": "#fitBtn \"ALL\"", "by": "#aConvo \"What’s next?First up: Ski Proclou (green\""}; {"el": "#dimBtn \"3D\"", "by": "#aConvo \"What’s next?First up: Ski Proclou (green\""}; {"el": "#placesBtn \"Places on the map\"", "by": "#aConvo \"What’s next?First up: Ski Proclou (green\""}; {"el": "#goBtn \"Start skiing\"", "by": "#aSugs \"What’s next?Where’s lunch?Any lifts clos\""}; {"el": "#stepsBtn \"Steps\"", "by": "#aHold \"Tap and talk\""}; {"el": "#progBtn \"Runs\"", "by": "#aHold \"Tap and talk\""}
- Crowded: {"a": "#followBtn \"ME\"", "b": "#aClose \"Close\"", "gap": -33}; {"a": "#compassBtn \"Compass\"", "b": "#aClose \"Close\"", "gap": -1}; {"a": "#goBtn \"Start skiing\"", "b": "button \"How much today?\"", "gap": -40}; {"a": "#goBtn \"Start skiing\"", "b": "button \"Call the group\"", "gap": -40}; {"a": "#goBtn \"Start skiing\"", "b": "#aHold \"Tap and talk\"", "gap": -12}; {"a": "#stepsBtn \"Steps\"", "b": "#aHold \"Tap and talk\"", "gap": -50}; {"a": "#progBtn \"Runs\"", "b": "#aHold \"Tap and talk\"", "gap": -50}

## web-iphoneSE

Tour finished: yes · checks 30/30 passed · layout issues 26 · JS/app errors 0 · screenshots 19

### Behaviour checks

- PASS page loads and map is ready (index.html): 79 steps
- PASS gear opens settings
- PASS settings fit without scrolling: 611 vs 611
- PASS week fits without scrolling: 608 vs 608
- PASS Follow the plan toggle works (off by default): false -> true -> false
- PASS menu lists the days: 6 day buttons
- PASS tapping Day 2 switches the plan: Avoriaz -> Morzine + Les Gets
- PASS menu closes
- PASS live lift status loads from the internet: 7 of 182 open
- PASS guide button opens the morning brief: Morning! Day one. The mountain doesn't know what's coming. What are we doing tod
- PASS Today sheet opens
- PASS Ask answers a question: First up: Ski Proclou (green), planned for 9:00.Steps
- PASS steps sheet closes
- PASS next and previous step buttons: 0 -> 1 -> 0
- PASS Remaining filter chip toggles
- PASS Runs view returns to route
- PASS tracking shows the stats card
- PASS Sun mode switches on
- PASS trail of where you have been is recorded: 1221 trail points
- PASS free ski by default: no off-route banner: hidden
- PASS test replay moves the skier and counts km: km=9.92 max=52 step 0->10 pill="Test replay"
- PASS Plan from here builds a connected route: {"routed":1,"rejoin":11,"minutes":1} max gap 52 m
- PASS Plan from here explains what it did: New route from where you are: 1 step (about 1 min), then back on the plan at Prodains Express 3S gondola. They start at 
- PASS day recap shows the day: km=10.0 vert=155 top=52 lifts=4 goal=1 of 62 +1 today
- PASS home sheet is back after stopping: Avoriaz
- PASS stop & reset clears the replay: km=0.00
- PASS following link: nyc.html
- PASS page loads and map is ready (nyc.html): 8 steps
- PASS Practice in NYC link opens the NYC map: nyc.html
- PASS NYC page has a working way back: index.html

### Layout per screen

| screen | page | targets | too small (<44) | glove (<52) | covered | offscreen | sideways scroll | tiny text (<12px) | crowded |
|---|---|---|---|---|---|---|---|---|---|
| main | index.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| menu | index.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| menu-settings | index.html | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| brief | index.html | 15 | 0 | 0 | 10 | 0 | 0 | 3 | 6 |
| today | index.html | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| ask | index.html | 19 | 6 | 0 | 10 | 0 | 0 | 0 | 7 |
| steps | index.html | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| progress | index.html | 14 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| runs-list | index.html | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| places | index.html | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| map-3d | index.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| map-all | index.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| test-mode | index.html | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay | index.html | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay-sun | index.html | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| plan-from-here | index.html | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| recap | index.html | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| nyc-main | nyc.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| nyc-menu | nyc.html | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

#### brief
- Covered (tap goes elsewhere): {"el": "#menuBtn \"Week, places and settings\"", "by": "#bEyebrow \"SUN JAN 17 · MORNING BRIEF\""}; {"el": "#wxPill \"Today's brief: the day, weather, what to\"", "by": "#bEyebrow \"SUN JAN 17 · MORNING BRIEF\""}; {"el": "#followBtn \"ME\"", "by": "#bClose \"Close\""}; {"el": "#compassBtn \"Compass\"", "by": "div.gstage"}; {"el": "#fitBtn \"ALL\"", "by": "div.gstage"}; {"el": "#dimBtn \"3D\"", "by": "div.gstage"}; {"el": "#placesBtn \"Places on the map\"", "by": "#bCap \"Morning! Day one. The mountain doesn't k\""}; {"el": "#goBtn \"Start skiing\"", "by": "#bAsk \"Ask\""}; {"el": "#stepsBtn \"Steps\"", "by": "#bToday \"Weather and lifts in detail\""}; {"el": "#progBtn \"Runs\"", "by": "#bToday \"Weather and lifts in detail\""}
- Tiny text: {"el": "span \"24 lifts\"", "px": 11.52}; {"el": "span \"First move\"", "px": 11.52}; {"el": "span \"Partly cloudy\"", "px": 11.52}
- Crowded: {"a": "#followBtn \"ME\"", "b": "#bClose \"Close\"", "gap": -46}; {"a": "#goBtn \"Start skiing\"", "b": "#bPause \"Pause\"", "gap": -50}; {"a": "#goBtn \"Start skiing\"", "b": "#bAsk \"Ask\"", "gap": -50}; {"a": "#goBtn \"Start skiing\"", "b": "#bGo \"Start skiing\"", "gap": -50}; {"a": "#stepsBtn \"Steps\"", "b": "#bToday \"Weather and lifts in detail\"", "gap": -48}; {"a": "#progBtn \"Runs\"", "b": "#bToday \"Weather and lifts in detail\"", "gap": -48}

#### ask
- Too small: {"el": "button \"What’s next?\"", "w": 142, "h": 40}; {"el": "button \"Where’s lunch?\"", "w": 161, "h": 40}; {"el": "button \"Any lifts closed?\"", "w": 170, "h": 40}; {"el": "button \"Plan from here\"", "w": 157, "h": 40}; {"el": "button \"How much today?\"", "w": 181, "h": 40}; {"el": "button \"Call the group\"", "w": 151, "h": 40}
- Covered (tap goes elsewhere): {"el": "#menuBtn \"Week, places and settings\"", "by": "rect"}; {"el": "#wxPill \"Today's brief: the day, weather, what to\"", "by": "span \"Ask me anything about todayWorks on your\""}; {"el": "#followBtn \"ME\"", "by": "#aClose \"Close\""}; {"el": "#compassBtn \"Compass\"", "by": "#aConvo \"What’s next?First up: Ski Proclou (green\""}; {"el": "#fitBtn \"ALL\"", "by": "#aConvo \"What’s next?First up: Ski Proclou (green\""}; {"el": "#dimBtn \"3D\"", "by": "#aConvo \"What’s next?First up: Ski Proclou (green\""}; {"el": "#placesBtn \"Places on the map\"", "by": "#aConvo \"What’s next?First up: Ski Proclou (green\""}; {"el": "#goBtn \"Start skiing\"", "by": "button \"How much today?\""}; {"el": "#stepsBtn \"Steps\"", "by": "#aHold \"Tap and talk\""}; {"el": "#progBtn \"Runs\"", "by": "#aHold \"Tap and talk\""}
- Crowded: {"a": "#followBtn \"ME\"", "b": "#aClose \"Close\"", "gap": -33}; {"a": "#compassBtn \"Compass\"", "b": "#aClose \"Close\"", "gap": -1}; {"a": "#goBtn \"Start skiing\"", "b": "button \"How much today?\"", "gap": -40}; {"a": "#goBtn \"Start skiing\"", "b": "button \"Call the group\"", "gap": -40}; {"a": "#goBtn \"Start skiing\"", "b": "#aHold \"Tap and talk\"", "gap": -12}; {"a": "#stepsBtn \"Steps\"", "b": "#aHold \"Tap and talk\"", "gap": -50}; {"a": "#progBtn \"Runs\"", "b": "#aHold \"Tap and talk\"", "gap": -50}

## web-lines

Tour finished: yes · checks 17/17 passed · layout issues 0 · JS/app errors 0 · screenshots 4

### Behaviour checks

- PASS daily steps found (first lift in the morning, home run): [0, 1, 77, 76]
- PASS daily steps fold into one row each in Steps: 2
- PASS morning row says it is the same every day: Every morning: Proclou → Proclou chair | Same every day · 2 steps · tap to see | 9:00 | 3.2 km
- PASS tapping the row shows the steps
- PASS replay moved along the plan: step 6
- PASS done steps are drawn filled in (not removed): 8
- PASS steps ahead are drawn as an outline
- PASS daily steps are marked
- PASS cafes and restaurants hide while tracking: ["all",["in",["get","c"],["literal",["none"]]],["any",["==",["get","mtn"],1],["!
- PASS only the next step is labelled while tracking: ['Next · Crête']
- PASS done today chip shows: 5 of 78 done · 1 red
- PASS your track is drawn above the route
- PASS step numbers come back when you stop: 53
- PASS Stop then Start leaves a gap, no straight line across town: 2 pieces, longest hop 39 m
- PASS a GPS jump while tracking also leaves a gap: 3 pieces
- PASS clear asks for a second tap
- PASS Clear tracking history empties the track and the saved days: 15 -> 0 points, saved days [[0,0]]

### Layout per screen

| screen | page | targets | too small (<44) | glove (<52) | covered | offscreen | sideways scroll | tiny text (<12px) | crowded |
|---|---|---|---|---|---|---|---|---|---|
