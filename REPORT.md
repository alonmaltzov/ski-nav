# Ski Nav QA report

**Overall: 65 issue(s)**

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

Tour finished: yes · checks 45/47 passed · layout issues 19 · JS/app errors 0 · screenshots 31

### Behaviour checks

- PASS page loads and map is ready (index.html): 79 steps
- PASS gear opens settings
- **FAIL** settings fit without scrolling: 833 vs 770
- **FAIL** week fits without scrolling: 796 vs 770
- PASS Follow the plan toggle works (off by default): false -> true -> false
- PASS menu lists the days: 6 day buttons
- PASS tapping Day 2 switches the plan: Avoriaz -> Morzine + Les Gets
- PASS menu closes
- PASS live lift status loads from the internet: 9 of 182 open
- PASS guide button opens the morning brief: Morning. Day one. Fresh legs, zero excuses. Avoriaz today. 57 k, Folie Douce by 
- PASS Today sheet opens
- PASS Ask answers a question: First up: Ski Proclou (green), planned for 9:00.Steps
- PASS steps sheet closes
- PASS next and previous step buttons: 0 -> 1 -> 0
- PASS Runs has a clear way back to today: Today
- PASS Remaining filter chip toggles
- PASS ‹ Today returns to the day plan
- PASS Places stays open when you tap inside it
- PASS Places closes when you tap outside it
- PASS Places has a close button
- PASS tracking shows the stats card
- PASS Sun mode switches on
- PASS trail of where you have been is recorded: 932 trail points
- PASS free ski by default: no off-route banner: hidden
- PASS test replay moves the skier and counts km: km=6.80 max=52 step 0->7 pill="Test replay"
- PASS Plan from here builds a connected route: {"routed":1,"rejoin":8,"minutes":2} max gap 52 m
- PASS Plan from here explains what it did: New route from where you are: 1 step (about 2 min), then back on the plan at Jean Vuarnet (red). They start at step 8 be
- PASS day recap shows the day: km=9.1 vert=161 top=52 lifts=3 goal=1 of 100 +1 today
- PASS home sheet is back after stopping: Avoriaz
- PASS stop & reset clears the replay: km=0.00
- PASS ME shows my location without tracking: blue dot on map
- PASS compass button responds: pressed=false (no compass on this device, turned itself off)
- PASS native GPS fixes arrive: 29 fixes, raw path 318 m, speeds none, acc 5 m, alt undefined
- PASS simulator route is moving (test harness): 29 fixes, raw path 318 m, speeds none, acc 5 m, alt undefined
- PASS moving GPS turns into km and speed: km=0.31 speed=34 max=44 pill="GPS ±5 m" vs raw path 318 m
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
| menu | index.html | 11 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| menu-settings | index.html | 16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| brief | index.html | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| today | index.html | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| ask | index.html | 19 | 6 | 0 | 10 | 0 | 0 | 0 | 7 |
| steps | index.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| progress | index.html | 17 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| runs-list | index.html | 11 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| places | index.html | 16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| map-3d | index.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| map-all | index.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| test-mode | index.html | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay | index.html | 7 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay-sun | index.html | 7 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| plan-from-here | index.html | 8 | 0 | 0 | 0 | 0 | 0 | 4 | 0 |
| recap | index.html | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| me-button | index.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| gps-tracking | index.html | 7 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| nyc-main | nyc.html | 10 | 0 | 7 | 0 | 0 | 0 | 0 | 0 |
| nyc-menu | nyc.html | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

#### ask
- Too small: {"el": "button \"What’s next?\"", "w": 124, "h": 40}; {"el": "button \"Where’s lunch?\"", "w": 141, "h": 40}; {"el": "button \"Any lifts closed?\"", "w": 149, "h": 40}; {"el": "button \"Plan from here\"", "w": 136, "h": 40}; {"el": "button \"How much today?\"", "w": 159, "h": 40}; {"el": "button \"Call the group\"", "w": 131, "h": 40}
- Covered (tap goes elsewhere): {"el": "#menuBtn \"Week, places and settings\"", "by": "#aFace"}; {"el": "#wxPill \"Today's brief: the day, weather, what to\"", "by": "span \"Ask me anything about todayWorks on your\""}; {"el": "#followBtn \"ME\"", "by": "#aClose \"Close\""}; {"el": "#compassBtn \"Compass\"", "by": "#aConvo \"What’s next?First up: Ski Proclou (green\""}; {"el": "#fitBtn \"ALL\"", "by": "#aConvo \"What’s next?First up: Ski Proclou (green\""}; {"el": "#dimBtn \"3D\"", "by": "div.abub.it \"First up: Ski Proclou (green), planned f\""}; {"el": "#kingBtn \"Speed King: no top speeds yet today\"", "by": "#aConvo \"What’s next?First up: Ski Proclou (green\""}; {"el": "#stopBtn \"STOPPP: 0 of 3 today\"", "by": "#aConvo \"What’s next?First up: Ski Proclou (green\""}; {"el": "#goBtn \"Start skiing\"", "by": "#aHold \"Tap and talk\""}; {"el": "#stepsBtn \"Steps\"", "by": "#aHold \"Tap and talk\""}
- Crowded: {"a": "#followBtn \"ME\"", "b": "#aClose \"Close\"", "gap": -49}; {"a": "#compassBtn \"Compass\"", "b": "#aClose \"Close\"", "gap": -7}; {"a": "#goBtn \"Start skiing\"", "b": "button \"How much today?\"", "gap": -11}; {"a": "#goBtn \"Start skiing\"", "b": "button \"Call the group\"", "gap": -11}; {"a": "#goBtn \"Start skiing\"", "b": "#aHold \"Tap and talk\"", "gap": -63}; {"a": "#stepsBtn \"Steps\"", "b": "button \"Call the group\"", "gap": -11}; {"a": "#stepsBtn \"Steps\"", "b": "#aHold \"Tap and talk\"", "gap": -63}

#### replay
- Too small: {"el": "#spGrab \"Steps\"", "w": 352, "h": 24}

#### replay-sun
- Too small: {"el": "#spGrab \"Steps\"", "w": 348, "h": 24}

#### plan-from-here
- Tiny text: {"el": "span \"Max\"", "px": 11.52}; {"el": "span \"Km\"", "px": 11.52}; {"el": "span \"Vert m\"", "px": 11.52}; {"el": "span \"Time\"", "px": 11.52}

#### gps-tracking
- Too small: {"el": "#spGrab \"Steps\"", "w": 352, "h": 24}

#### nyc-main
- Small for gloves: {"el": "#menuBtn \"Week, places and settings\"", "w": 50, "h": 50, "want": 60}; {"el": "#wxPill \"Today's brief: the day, weather, what to\"", "w": 131, "h": 50, "want": 60}; {"el": "#followBtn \"ME\"", "w": 50, "h": 50, "want": 60}; {"el": "#compassBtn \"Compass\"", "w": 50, "h": 50, "want": 60}; {"el": "#fitBtn \"ALL\"", "w": 50, "h": 50, "want": 60}; {"el": "#dimBtn \"3D\"", "w": 50, "h": 50, "want": 60}; {"el": "#stepsBtn \"Steps\"", "w": 180, "h": 56, "want": 60}

## web-galaxyS24

Tour finished: yes · checks 34/34 passed · layout issues 18 · JS/app errors 0 · screenshots 19

### Behaviour checks

- PASS page loads and map is ready (index.html): 79 steps
- PASS gear opens settings
- PASS settings fit without scrolling: 724 vs 724
- PASS week fits without scrolling: 677 vs 677
- PASS Follow the plan toggle works (off by default): false -> true -> false
- PASS menu lists the days: 6 day buttons
- PASS tapping Day 2 switches the plan: Avoriaz -> Morzine + Les Gets
- PASS menu closes
- PASS live lift status loads from the internet: 9 of 182 open
- PASS guide button opens the morning brief: Morning. Day one. Fresh legs, zero excuses. Avoriaz today. 57 k, Folie Douce by 
- PASS Today sheet opens
- PASS Ask answers a question: First up: Ski Proclou (green), planned for 9:00.Steps
- PASS steps sheet closes
- PASS next and previous step buttons: 0 -> 1 -> 0
- PASS Runs has a clear way back to today: Today
- PASS Remaining filter chip toggles
- PASS ‹ Today returns to the day plan
- PASS Places stays open when you tap inside it
- PASS Places closes when you tap outside it
- PASS Places has a close button
- PASS tracking shows the stats card
- PASS Sun mode switches on
- PASS trail of where you have been is recorded: 1532 trail points
- PASS free ski by default: no off-route banner: hidden
- PASS test replay moves the skier and counts km: km=11.30 max=52 step 0->13 pill="Test replay"
- PASS Plan from here builds a connected route: {"routed":1,"rejoin":14,"minutes":5} max gap 52 m
- PASS Plan from here explains what it did: New route from where you are: 1 step (about 5 min), then back on the plan at Jean Vuarnet (red). They start at step 14 b
- PASS day recap shows the day: km=15.6 vert=160 top=52 lifts=7 goal=2 of 100 +2 today
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
| menu | index.html | 11 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| menu-settings | index.html | 16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| brief | index.html | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| today | index.html | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| ask | index.html | 19 | 6 | 0 | 10 | 0 | 0 | 0 | 5 |
| steps | index.html | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| progress | index.html | 16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| runs-list | index.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| places | index.html | 16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| map-3d | index.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| map-all | index.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| test-mode | index.html | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay | index.html | 7 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay-sun | index.html | 7 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| plan-from-here | index.html | 6 | 0 | 0 | 0 | 0 | 0 | 4 | 0 |
| recap | index.html | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| nyc-main | nyc.html | 10 | 0 | 7 | 0 | 0 | 0 | 0 | 0 |
| nyc-menu | nyc.html | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

#### ask
- Too small: {"el": "button \"What’s next?\"", "w": 142, "h": 40}; {"el": "button \"Where’s lunch?\"", "w": 161, "h": 40}; {"el": "button \"Any lifts closed?\"", "w": 170, "h": 40}; {"el": "button \"Plan from here\"", "w": 157, "h": 40}; {"el": "button \"How much today?\"", "w": 181, "h": 40}; {"el": "button \"Call the group\"", "w": 151, "h": 40}
- Covered (tap goes elsewhere): {"el": "#menuBtn \"Week, places and settings\"", "by": "#aFace"}; {"el": "#wxPill \"Today's brief: the day, weather, what to\"", "by": "#aState \"Ask me anything about today\""}; {"el": "#followBtn \"ME\"", "by": "#aClose \"Close\""}; {"el": "#compassBtn \"Compass\"", "by": "div.abub.me \"What’s next?\""}; {"el": "#fitBtn \"ALL\"", "by": "div.abub.it \"First up: Ski Proclou (green), planned f\""}; {"el": "#dimBtn \"3D\"", "by": "div.abub.it \"First up: Ski Proclou (green), planned f\""}; {"el": "#kingBtn \"Speed King: no top speeds yet today\"", "by": "div.abub.it \"First up: Ski Proclou (green), planned f\""}; {"el": "#stopBtn \"STOPPP: 0 of 3 today\"", "by": "#aConvo \"What’s next?First up: Ski Proclou (green\""}; {"el": "#goBtn \"Start skiing\"", "by": "#aHold \"Tap and talk\""}; {"el": "#stepsBtn \"Steps\"", "by": "#aHold \"Tap and talk\""}
- Crowded: {"a": "#followBtn \"ME\"", "b": "#aClose \"Close\"", "gap": -51}; {"a": "#compassBtn \"Compass\"", "b": "#aClose \"Close\"", "gap": -5}; {"a": "#goBtn \"Start skiing\"", "b": "button \"Call the group\"", "gap": -11}; {"a": "#goBtn \"Start skiing\"", "b": "#aHold \"Tap and talk\"", "gap": -63}; {"a": "#stepsBtn \"Steps\"", "b": "#aHold \"Tap and talk\"", "gap": -63}

#### replay
- Too small: {"el": "#spGrab \"Steps\"", "w": 318, "h": 24}

#### replay-sun
- Too small: {"el": "#spGrab \"Steps\"", "w": 314, "h": 24}

#### plan-from-here
- Tiny text: {"el": "span \"Max\"", "px": 11.52}; {"el": "span \"Km\"", "px": 11.52}; {"el": "span \"Vert m\"", "px": 11.52}; {"el": "span \"Time\"", "px": 11.52}

#### nyc-main
- Small for gloves: {"el": "#menuBtn \"Week, places and settings\"", "w": 50, "h": 50, "want": 60}; {"el": "#wxPill \"Today's brief: the day, weather, what to\"", "w": 140, "h": 50, "want": 60}; {"el": "#followBtn \"ME\"", "w": 50, "h": 50, "want": 60}; {"el": "#compassBtn \"Compass\"", "w": 50, "h": 50, "want": 60}; {"el": "#fitBtn \"ALL\"", "w": 50, "h": 50, "want": 60}; {"el": "#dimBtn \"3D\"", "w": 50, "h": 50, "want": 60}; {"el": "#stepsBtn \"Steps\"", "w": 159, "h": 56, "want": 60}

## web-games

Tour finished: **NO** · checks 16/16 passed · layout issues 0 · JS/app errors 0 · screenshots 4

### Behaviour checks

- PASS 3 STOPPPs a day: [{'n': 1, 'h': 12.133333333333333, 'who': 'You'}, {'n': 2, 'h': 12.6, 'who': 'You'}, {'n': 3, 'h': 13.666666666666666, 'who': 'You'}]
- PASS all between 11:00 and 15:00: [12.13, 12.6, 13.67]
- PASS same times every time it is worked out
- PASS STOPPP shows after 3 minutes on a lift: You
- PASS only one STOPPP fires: {"2027-01-19":[1]}
- PASS the same STOPPP does not fire twice
- PASS no passport race popup on the first crossing
- PASS STOPPP button shows today's count: 1/3
- PASS STOPPP button opens today's 3 rounds
- PASS Try it now: a test STOPPP that says so: Test run · doesn’t count
- PASS the test doesn't count
- PASS "Not me today" on a test keeps you in the rounds
- PASS Speed King podium: You hit 74 km/h. Top speed counts on reds and blues only.
- PASS Settings > Games lists today’s rounds
- PASS STOPPP can be switched off
- PASS no page errors: []

### Layout per screen

| screen | page | targets | too small (<44) | glove (<52) | covered | offscreen | sideways scroll | tiny text (<12px) | crowded |
|---|---|---|---|---|---|---|---|---|---|

## web-group

Tour finished: yes · checks 53/53 passed · layout issues 0 · JS/app errors 0 · screenshots 19

### Behaviour checks

- PASS people button is in the menu
- PASS organizer creates the trip: AVZ-E526
- PASS invite link shows the code: https://alonmaltzov.github.io/ski-nav/join.html?c=AVZ-E526
- PASS copy puts the invite link on the clipboard: https://alonmaltzov.github.io/ski-nav/join.html?c=AVZ-E526
- PASS organizer sees the group call setup
- PASS a bad WhatsApp link is refused
- PASS organizer saves the WhatsApp group link
- PASS a non-Splitwise link is refused
- PASS organizer saves the Splitwise link
- PASS join screen shows who invited you: Alon invited you to
- PASS Continue is off until a name is typed
- PASS friend joins the trip: ['Alon', 'Dana Levi']
- PASS friend gets "Call the crew" in Shai's hub
- PASS friend gets Splitwise in Shai's hub
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
- PASS invite page on iPhone opens the app: skinav://join?c=AVZ-E526
- PASS invite page on iPhone links to TestFlight: https://testflight.apple.com/join/kPyVvmk9
- PASS invite page (iphone) has no browser option (apps only)
- PASS invite page on Android opens the app (or downloads it): intent://join?c=AVZ-E526#Intent;scheme=skinav;package=com.alonmaltzov.skinav;S.browser_fallback_url=https%3A%2F%2Fgithub
- PASS invite page on Android downloads the app when missing
- PASS invite page (android) has no browser option (apps only)

### Layout per screen

| screen | page | targets | too small (<44) | glove (<52) | covered | offscreen | sideways scroll | tiny text (<12px) | crowded |
|---|---|---|---|---|---|---|---|---|---|

## web-iphone16

Tour finished: yes · checks 34/34 passed · layout issues 21 · JS/app errors 0 · screenshots 19

### Behaviour checks

- PASS page loads and map is ready (index.html): 79 steps
- PASS gear opens settings
- PASS settings fit without scrolling: 796 vs 796
- PASS week fits without scrolling: 775 vs 775
- PASS Follow the plan toggle works (off by default): false -> true -> false
- PASS menu lists the days: 6 day buttons
- PASS tapping Day 2 switches the plan: Avoriaz -> Morzine + Les Gets
- PASS menu closes
- PASS live lift status loads from the internet: 9 of 182 open
- PASS guide button opens the morning brief: Morning. Day one. Fresh legs, zero excuses. Avoriaz today. 57 k, Folie Douce by 
- PASS Today sheet opens
- PASS Ask answers a question: First up: Ski Proclou (green), planned for 9:00.Steps
- PASS steps sheet closes
- PASS next and previous step buttons: 0 -> 1 -> 0
- PASS Runs has a clear way back to today: Today
- PASS Remaining filter chip toggles
- PASS ‹ Today returns to the day plan
- PASS Places stays open when you tap inside it
- PASS Places closes when you tap outside it
- PASS Places has a close button
- PASS tracking shows the stats card
- PASS Sun mode switches on
- PASS trail of where you have been is recorded: 1795 trail points
- PASS free ski by default: no off-route banner: hidden
- PASS test replay moves the skier and counts km: km=13.19 max=52 step 0->14 pill="Test replay"
- PASS Plan from here builds a connected route: {"routed":1,"rejoin":15,"minutes":1} max gap 52 m
- PASS Plan from here explains what it did: New route from where you are: 1 step (about 1 min), then back on the plan at Le Crôt Variante (blue) → Crôt (blue) → Cro
- PASS day recap shows the day: km=17.6 vert=157 top=53 lifts=7 goal=3 of 100 +3 today
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
| menu | index.html | 11 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| menu-settings | index.html | 16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| brief | index.html | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| today | index.html | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| ask | index.html | 19 | 6 | 0 | 10 | 0 | 0 | 0 | 7 |
| steps | index.html | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| progress | index.html | 17 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| runs-list | index.html | 11 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| places | index.html | 16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| map-3d | index.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| map-all | index.html | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| test-mode | index.html | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay | index.html | 7 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| replay-sun | index.html | 7 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| plan-from-here | index.html | 7 | 0 | 0 | 0 | 0 | 0 | 4 | 0 |
| recap | index.html | 3 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |
| nyc-main | nyc.html | 10 | 0 | 7 | 0 | 0 | 0 | 0 | 0 |
| nyc-menu | nyc.html | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

#### ask
- Too small: {"el": "button \"What’s next?\"", "w": 142, "h": 40}; {"el": "button \"Where’s lunch?\"", "w": 161, "h": 40}; {"el": "button \"Any lifts closed?\"", "w": 170, "h": 40}; {"el": "button \"Plan from here\"", "w": 157, "h": 40}; {"el": "button \"How much today?\"", "w": 181, "h": 40}; {"el": "button \"Call the group\"", "w": 151, "h": 40}
- Covered (tap goes elsewhere): {"el": "#menuBtn \"Week, places and settings\"", "by": "#aFace"}; {"el": "#wxPill \"Today's brief: the day, weather, what to\"", "by": "span \"Ask me anything about todayWorks on your\""}; {"el": "#followBtn \"ME\"", "by": "#aClose \"Close\""}; {"el": "#compassBtn \"Compass\"", "by": "div.abub.me \"What’s next?\""}; {"el": "#fitBtn \"ALL\"", "by": "#aConvo \"What’s next?First up: Ski Proclou (green\""}; {"el": "#dimBtn \"3D\"", "by": "div.abub.it \"First up: Ski Proclou (green), planned f\""}; {"el": "#kingBtn \"Speed King: no top speeds yet today\"", "by": "div.abub.it \"First up: Ski Proclou (green), planned f\""}; {"el": "#stopBtn \"STOPPP: 0 of 3 today\"", "by": "#aConvo \"What’s next?First up: Ski Proclou (green\""}; {"el": "#goBtn \"Start skiing\"", "by": "#aHold \"Tap and talk\""}; {"el": "#stepsBtn \"Steps\"", "by": "#aHold \"Tap and talk\""}
- Crowded: {"a": "#followBtn \"ME\"", "b": "#aClose \"Close\"", "gap": -51}; {"a": "#compassBtn \"Compass\"", "b": "#aClose \"Close\"", "gap": -5}; {"a": "#goBtn \"Start skiing\"", "b": "button \"How much today?\"", "gap": -11}; {"a": "#goBtn \"Start skiing\"", "b": "button \"Call the group\"", "gap": -11}; {"a": "#goBtn \"Start skiing\"", "b": "#aHold \"Tap and talk\"", "gap": -63}; {"a": "#stepsBtn \"Steps\"", "b": "button \"Call the group\"", "gap": -11}; {"a": "#stepsBtn \"Steps\"", "b": "#aHold \"Tap and talk\"", "gap": -63}

#### replay
- Too small: {"el": "#spGrab \"Steps\"", "w": 343, "h": 24}

#### replay-sun
- Too small: {"el": "#spGrab \"Steps\"", "w": 339, "h": 24}

#### plan-from-here
- Tiny text: {"el": "span \"Max\"", "px": 11.52}; {"el": "span \"Km\"", "px": 11.52}; {"el": "span \"Vert m\"", "px": 11.52}; {"el": "span \"Time\"", "px": 11.52}

#### recap
- Covered (tap goes elsewhere): {"el": "#recapClose \"Done\"", "by": "div.gzbig \"STOPPP\""}; {"el": "#recapShare \"Share day\"", "by": "#stopSkip \"Not me today\""}; {"el": "#recapNext \"Plan tomorrow\"", "by": "#stopOk \"Cheers 🥃\""}

#### nyc-main
- Small for gloves: {"el": "#menuBtn \"Week, places and settings\"", "w": 50, "h": 50, "want": 60}; {"el": "#wxPill \"Today's brief: the day, weather, what to\"", "w": 140, "h": 50, "want": 60}; {"el": "#followBtn \"ME\"", "w": 50, "h": 50, "want": 60}; {"el": "#compassBtn \"Compass\"", "w": 50, "h": 50, "want": 60}; {"el": "#fitBtn \"ALL\"", "w": 50, "h": 50, "want": 60}; {"el": "#dimBtn \"3D\"", "w": 50, "h": 50, "want": 60}; {"el": "#stepsBtn \"Steps\"", "w": 176, "h": 56, "want": 60}

## web-lines

Tour finished: yes · checks 17/17 passed · layout issues 0 · JS/app errors 0 · screenshots 4

### Behaviour checks

- PASS daily steps found (first lift in the morning, home run): [0, 1, 77, 76]
- PASS daily steps fold into one row each in Steps: 2
- PASS morning row says it is the same every day: Every morning: Proclou → Proclou chair | Same every day · 2 steps · tap to see | 9:00 | 3.2 km
- PASS tapping the row shows the steps
- PASS replay moved along the plan: step 6
- PASS done steps are drawn filled in (not removed): 7
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

## web-passport

Tour finished: **NO** · checks 17/17 passed · layout issues 0 · JS/app errors 0 · screenshots 3

### Behaviour checks

- PASS not a trip day: no check on open
- PASS the menu marks days 3, 4 and 6 as Swiss: [False, False, True, True, False, True]
- PASS French day: no check
- PASS French day: Start skiing is not locked
- PASS Swiss day: the passport check opens
- PASS Swiss day: Start skiing is locked, Passport check sits above it
- PASS a locked Start skiing opens the check instead of starting
- PASS the passport clip plays
- PASS it does not close by tapping or Escape
- PASS half a slide does not count
- PASS a full slide confirms
- PASS Start skiing sits right in the crew sheet
- PASS remembered for the day: 2027-01-19
- PASS after the slide, Start skiing unlocks
- PASS once checked, it stays away
- PASS a nudge brings the check back: Avsha says: passport. Now.
- PASS no page errors: []

### Layout per screen

| screen | page | targets | too small (<44) | glove (<52) | covered | offscreen | sideways scroll | tiny text (<12px) | crowded |
|---|---|---|---|---|---|---|---|---|---|

## web-sfx

Tour finished: **NO** · checks 24/24 passed · layout issues 0 · JS/app errors 0 · screenshots 1

### Behaviour checks

- PASS all 9 clips are in the page: ['brief', 'closed', 'passport', 'speedking', 'start', 'steps', 'stop', 'stoppp', 'today']
- PASS clips decode: 2.07
- PASS opening the app is quiet now: []
- PASS the menu button plays today's plan: ['today']
- PASS every time: ['today', 'today']
- PASS picking a Swiss day plays the passport clip, a French day does not: [['passport'], []]
- PASS Steps plays its clip: ['steps']
- PASS Shai's lines wait for the clip to finish
- PASS then all of them show at once
- PASS every brief plays the clip: [['brief'], ['brief', 'brief']]
- PASS Start skiing plays its clip: ['start']
- PASS while skiing, Stop is a big Hold button: {'x': 288, 'y': 746.6875, 'width': 80, 'height': 80}
- PASS a short tap does not stop
- PASS holding 1.5 s stops, with its clip: ['start', 'stop']
- PASS STOPPP plays its clip: ['stoppp']
- PASS Speed King plays its clip (passport moved to picking the day): ['speedking']
- PASS a plan lift closing plays the change-of-plan clip, once: [['closed'], ['closed']]
- PASS Lifts button: says which plan lift is closed, with the clip: ['Proclou chair is shut. Plan from here fixes it.', ['closed']]
- PASS Lifts button opens the lift list
- PASS Lifts button plays the clip every tap, even with nothing closed: ['closed', 'closed']
- PASS a plan lift closing plays the change-of-plan clip, once: [['closed'], ['closed']]
- PASS Plan from here plays the Steps clip: ['closed', 'closed', 'steps']
- PASS Sound clips off: nothing plays: []
- PASS no page errors: []

### Layout per screen

| screen | page | targets | too small (<44) | glove (<52) | covered | offscreen | sideways scroll | tiny text (<12px) | crowded |
|---|---|---|---|---|---|---|---|---|---|

## web-slopes

Tour finished: **NO** · checks 11/11 passed · layout issues 0 · JS/app errors 0 · screenshots 1

### Behaviour checks

- PASS slope status comes in with the lifts: {'sl': 293, 'open': 8}
- PASS most of today's runs are matched to the resort list: 29 of 33
- PASS whole area: lifts and slopes like the official site: 9/182 lifts · 8/293 slopes open
- PASS today's plan comes first, then the whole area: ['Today’s plan', 'Whole area']
- PASS the whole area opens into resorts: ['Avoriaz · 0/26 lifts · 0/41 slopes', 'Champéry · Les Crosets · 1/16 lifts · 0/17 slopes', 'Châtel · 0/32 lifts · 0/35 slopes', 'La Chapelle · 0/10 lifts · 0/11 slopes']
- PASS plan runs are listed with the lifts: 521
- PASS a run can be marked closed: [1, 'closed']
- PASS the guide names the closed run: Combe à Floret is shut. Plan from here fixes it.
- PASS the plan step for that run says closed: {'k': 2, 'cur': 0}
- PASS back online: checks again right away: 3 -> 4
- PASS no page errors: []

### Layout per screen

| screen | page | targets | too small (<44) | glove (<52) | covered | offscreen | sideways scroll | tiny text (<12px) | crowded |
|---|---|---|---|---|---|---|---|---|---|

## web-tour

Tour finished: **NO** · checks 41/41 passed · layout issues 0 · JS/app errors 0 · screenshots 14

### Behaviour checks

- PASS [iphone16] tour opens on first launch
- PASS [iphone16] no clip over the tour: []
- PASS [iphone16] step 1: bubble on screen, nothing it points at is covered: {'top': 250, 'bottom': 502.796875, 'h': 852, 'rings': 0, 'overlap': False}
- PASS [iphone16] step 1: button says Allow location: Allow location
- PASS [iphone16] step 2: bubble on screen, nothing it points at is covered: {'top': 346, 'bottom': 552.53125, 'h': 852, 'rings': 1, 'overlap': False}
- PASS [iphone16] step 2: button says Next: Next
- PASS [iphone16] step 3: bubble on screen, nothing it points at is covered: {'top': 490, 'bottom': 720.796875, 'h': 852, 'rings': 2, 'overlap': False}
- PASS [iphone16] step 3: button says Next: Next
- PASS [iphone16] step 4: bubble on screen, nothing it points at is covered: {'top': 116.265625, 'bottom': 347.0625, 'h': 852, 'rings': 2, 'overlap': False}
- PASS [iphone16] step 4: button says Next: Next
- PASS [iphone16] step 4 opens the week
- PASS [iphone16] step 5: bubble on screen, nothing it points at is covered: {'top': 468, 'bottom': 765.796875, 'h': 852, 'rings': 2, 'overlap': False}
- PASS [iphone16] step 5: button says Let’s ski: Let’s ski
- PASS [iphone16] Let’s ski closes the tour and remembers it
- PASS [iphone16] back on today, not the week
- PASS [iphone16] Replay the tour is in Settings (Tour button)
- PASS [iphone16] Replay starts at step 1
- PASS [iphone16] Skip on the week step closes the tour and the week
- PASS [iphone16] friends who join are greeted by name: Hey Dana! Shai here. Couldn’t make the trip, so I’m in your 
- PASS [iphone16] no page errors: []
- PASS [galaxyS24] tour opens on first launch
- PASS [galaxyS24] no clip over the tour: []
- PASS [galaxyS24] step 1: bubble on screen, nothing it points at is covered: {'top': 250, 'bottom': 502.796875, 'h': 780, 'rings': 0, 'overlap': False}
- PASS [galaxyS24] step 1: button says Allow location: Allow location
- PASS [galaxyS24] step 2: bubble on screen, nothing it points at is covered: {'top': 274, 'bottom': 480.53125, 'h': 780, 'rings': 1, 'overlap': False}
- PASS [galaxyS24] step 2: button says Next: Next
- PASS [galaxyS24] step 3: bubble on screen, nothing it points at is covered: {'top': 418, 'bottom': 648.796875, 'h': 780, 'rings': 2, 'overlap': False}
- PASS [galaxyS24] step 3: button says Next: Next
- PASS [galaxyS24] step 4: bubble on screen, nothing it points at is covered: {'top': 88.90625, 'bottom': 319.703125, 'h': 780, 'rings': 2, 'overlap': False}
- PASS [galaxyS24] step 4: button says Next: Next
- PASS [galaxyS24] step 4 opens the week
- PASS [galaxyS24] step 5: bubble on screen, nothing it points at is covered: {'top': 390, 'bottom': 712.0625, 'h': 780, 'rings': 2, 'overlap': False}
- PASS [galaxyS24] step 5: button says Let’s ski: Let’s ski
- PASS [galaxyS24] Let’s ski closes the tour and remembers it
- PASS [galaxyS24] back on today, not the week
- PASS [galaxyS24] Replay the tour is in Settings (Tour button)
- PASS [galaxyS24] Settings still fit without scrolling: [116.59375, 780]
- PASS [galaxyS24] Replay starts at step 1
- PASS [galaxyS24] Skip on the week step closes the tour and the week
- PASS [galaxyS24] friends who join are greeted by name: Hey Dana! Shai here. Couldn’t make the trip, so I’m in your 
- PASS [galaxyS24] no page errors: []

### Layout per screen

| screen | page | targets | too small (<44) | glove (<52) | covered | offscreen | sideways scroll | tiny text (<12px) | crowded |
|---|---|---|---|---|---|---|---|---|---|
