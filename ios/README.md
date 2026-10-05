# Ski Nav for iPhone + Apple Watch

The iPhone app runs the same Ski Nav you've been testing on the web, with native GPS that keeps
recording when the phone is locked in your pocket. The Watch app runs as a Downhill Skiing workout,
so GPS stays on with the screen off, and shows speed, km, max, vertical, LIFT and the next step.

## One-time setup on your Mac (about 30 minutes, mostly downloads)

1. **Xcode**: install from the Mac App Store (free, large download). Open it once and let it install
   the iOS and watchOS components it asks for.
2. **Homebrew** (skip if `brew` already works in Terminal):
   `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
3. In Terminal:
   ```
   git clone https://github.com/alonmaltzov/ski-nav
   cd ski-nav/ios
   ./setup.sh
   ```
   This installs XcodeGen, builds the Xcode project and opens it.
4. Xcode > Settings > Accounts > **+** > Apple ID. Sign in with your Apple ID.
5. In the left sidebar click **SkiNav** (blue icon) > target **SkiNav** > **Signing & Capabilities** >
   Team: pick your name. Repeat for target **SkiNavWatch**.
   If it says the bundle ID is taken, change `com.alonmaltzov` to something unique in both targets.

## Install on your iPhone and Watch

1. Plug the iPhone into the Mac with a cable and tap **Trust** on the phone.
2. iPhone: Settings > Privacy & Security > **Developer Mode** > On (it restarts).
   Do the same on the Watch: Settings > Privacy & Security > Developer Mode.
3. At the top of Xcode, choose your iPhone as the destination and press **Run** (the play button).
4. First launch only: iPhone Settings > General > VPN & Device Management > trust your Apple ID.
5. The Watch app installs with it. If it doesn't appear: iPhone Watch app > scroll to Ski Nav > Install.

## Using it

- iPhone: tap **Start tracking**. Allow location, then choose **Change to Always Allow** so it keeps
  tracking while locked.
- Watch: swipe up to the last page > **Start ski day**. Allow Health and location.
  The phone sends today's plan to the watch whenever you open Ski Nav on the phone.
- End of the day: Watch > **End ski day**. It saves as a Downhill Skiing workout in Fitness.

## Things to know

- With a free Apple ID the apps stop opening after **7 days**. Plug in and press Run again.
  Do this on Jan 15 or 16 so it lasts the whole trip.
- If Xcode shows a signing error about **HealthKit** on the Watch target, that feature needs the paid
  Apple Developer account ($99/yr). Either get it, or remove HealthKit and the watch will only track
  while its screen is on.
- After any update: `git pull`, then `./setup.sh`, then Run.
