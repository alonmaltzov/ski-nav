import AVFoundation
import Speech
import UserNotifications
#if canImport(FoundationModels)
import FoundationModels
#endif

/// The guide's iPhone side, all on the phone (no accounts, no paid services):
/// - speaks the morning brief and answers with the iPhone voice, or the user's Personal Voice
/// - listens with Apple's on-device speech recognition
/// - schedules the morning notification on trip days
/// - answers open questions with Apple's on-phone model when the iPhone has it (iOS 26, Apple Intelligence)
/// The page drives it with bridge commands (speak, listen, think, briefSchedule, personalVoice) and gets events back
/// through window.__guide.on({type: ...}).
final class Guide: NSObject, AVSpeechSynthesizerDelegate, UNUserNotificationCenterDelegate {
    static let shared = Guide()

    private let synth = AVSpeechSynthesizer()
    private var parts: [AVSpeechUtterance] = []
    /// set when the app was opened from the morning notification before the page was ready
    var pendingBrief = false

    override init() {
        super.init()
        synth.delegate = self
    }

    private func emit(_ obj: [String: Any]) {
        guard let d = try? JSONSerialization.data(withJSONObject: obj), let s = String(data: d, encoding: .utf8) else { return }
        WebBridge.shared.js("window.__guide && window.__guide.on(\(s))")
    }

    // MARK: Speaking

    func speak(_ body: [String: Any]) {
        if body["stop"] as? Bool == true { parts = []; synth.stopSpeaking(at: .immediate); return }
        if let p = body["pause"] as? Bool { if p { synth.pauseSpeaking(at: .word) } else { synth.continueSpeaking() }; return }
        guard let texts = body["parts"] as? [String], !texts.isEmpty else { return }
        stopListeningNow()
        synth.stopSpeaking(at: .immediate)
        let session = AVAudioSession.sharedInstance()
        try? session.setCategory(.playback, mode: .spokenAudio, options: [.duckOthers])
        try? session.setActive(true)
        let voice = pickVoice(personal: (body["voice"] as? String) == "personal")
        parts = texts.map { text in
            let u = AVSpeechUtterance(string: text)
            u.voice = voice
            u.rate = AVSpeechUtteranceDefaultSpeechRate
            u.postUtteranceDelay = 0.12
            return u
        }
        parts.forEach { synth.speak($0) }
    }

    /// Personal Voice when chosen and allowed, else the best-quality US English voice on the phone.
    private func pickVoice(personal: Bool) -> AVSpeechSynthesisVoice? {
        let all = AVSpeechSynthesisVoice.speechVoices()
        if personal, AVSpeechSynthesizer.personalVoiceAuthorizationStatus == .authorized,
           let v = all.first(where: { $0.voiceTraits.contains(.isPersonalVoice) }) {
            return v
        }
        let best = all.filter { $0.language == "en-US" && !$0.voiceTraits.contains(.isNoveltyVoice) }
            .max { $0.quality.rawValue < $1.quality.rawValue }
        return best ?? AVSpeechSynthesisVoice(language: "en-US")
    }

    func requestPersonalVoice() {
        AVSpeechSynthesizer.requestPersonalVoiceAuthorization { status in
            if status != .authorized {
                self.emit(["type": "error", "msg": "Personal Voice isn't set up yet. Make one in iPhone Settings › Accessibility › Personal Voice, then allow Ski Nav to use it. Until then I'll use the iPhone voice."])
            }
        }
    }

    func speechSynthesizer(_ s: AVSpeechSynthesizer, didStart u: AVSpeechUtterance) {
        if let i = parts.firstIndex(where: { $0 === u }) { emit(["type": "part", "i": i]) }
    }

    func speechSynthesizer(_ s: AVSpeechSynthesizer, didFinish u: AVSpeechUtterance) {
        guard u === parts.last else { return }
        parts = []
        emit(["type": "done"])
        try? AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)
    }

    // MARK: Listening (on-device speech to text)

    private let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
    private let engine = AVAudioEngine()
    private var request: SFSpeechAudioBufferRecognitionRequest?
    private var task: SFSpeechRecognitionTask?
    private var silence: Timer?

    func listen(_ on: Bool) {
        guard on else { finishListening(); return }
        SFSpeechRecognizer.requestAuthorization { status in
            DispatchQueue.main.async {
                guard status == .authorized else {
                    self.emit(["type": "error", "msg": "To talk to me, allow Speech Recognition for Ski Nav in Settings."]); return
                }
                AVAudioApplication.requestRecordPermission { ok in
                    DispatchQueue.main.async {
                        if ok { self.triedServer = false; self.startEngine() }
                        else { self.emit(["type": "error", "msg": "To talk to me, allow the Microphone for Ski Nav in Settings."]) }
                    }
                }
            }
        }
    }

    private var heardSomething = false
    private var triedServer = false

    private func startEngine(onDevice: Bool = true) {
        guard let rec = recognizer else {
            emit(["type": "error", "msg": "Speech recognition isn't available on this iPhone."]); return
        }
        guard rec.isAvailable else {
            emit(["type": "error", "msg": "Speech recognition isn't available right now. Check that Siri & Dictation is on in Settings, or tap a question below."]); return
        }
        synth.stopSpeaking(at: .immediate)
        task?.cancel(); task = nil
        if engine.isRunning { engine.stop(); engine.inputNode.removeTap(onBus: 0) }
        let session = AVAudioSession.sharedInstance()
        do {
            try session.setCategory(.playAndRecord, mode: .measurement, options: [.duckOthers, .defaultToSpeaker, .allowBluetooth])
            try session.setActive(true, options: .notifyOthersOnDeactivation)
        } catch {
            emit(["type": "error", "msg": "The microphone is busy (\(error.localizedDescription))."]); return
        }
        let req = SFSpeechAudioBufferRecognitionRequest()
        req.shouldReportPartialResults = true
        // on the phone first (private, works without signal); Apple's servers if the phone can't
        req.requiresOnDeviceRecognition = onDevice && rec.supportsOnDeviceRecognition
        request = req
        heardSomething = false
        let input = engine.inputNode
        input.removeTap(onBus: 0)
        let format = input.outputFormat(forBus: 0)
        guard format.sampleRate > 0, format.channelCount > 0 else {
            emit(["type": "error", "msg": "The microphone isn't giving any sound. Try again in a moment."]); request = nil; return
        }
        input.installTap(onBus: 0, bufferSize: 1024, format: format) { buffer, _ in req.append(buffer) }
        engine.prepare()
        do { try engine.start() } catch {
            emit(["type": "error", "msg": "The microphone couldn't start (\(error.localizedDescription))."]); request = nil; return
        }
        print("[app] listening (\(req.requiresOnDeviceRecognition ? "on the phone" : "Apple servers"))")
        emit(["type": "listening", "on": true])
        task = rec.recognitionTask(with: req) { [weak self] result, error in
            DispatchQueue.main.async {
                // ignore a task we already stopped or replaced (cancelling it reports an error too)
                guard let self, self.request === req else { return }
                if let r = result {
                    let text = r.bestTranscription.formattedString
                    if !text.isEmpty { self.heardSomething = true }
                    self.emit(["type": "heard", "text": text, "final": r.isFinal])
                    if r.isFinal { self.stopEngine() } else { self.armSilence(seconds: 1.6) }
                }
                if let e = error {
                    print("[app] speech error:", e.localizedDescription, (e as NSError).domain, (e as NSError).code)
                    let wasOnDevice = req.requiresOnDeviceRecognition
                    let heard = self.heardSomething
                    self.stopEngine()
                    if heard { return }
                    if wasOnDevice && !self.triedServer {
                        // the phone's own recognizer isn't ready (dictation model not downloaded): use Apple's
                        self.triedServer = true
                        self.startEngine(onDevice: false)
                    } else if (e as NSError).code != 216 && (e as NSError).code != 301 {   // 216/301 = we cancelled it
                        self.emit(["type": "error", "msg": "I couldn't hear that (\(e.localizedDescription)). Tap a question below, or try again."])
                    }
                }
            }
        }
        armSilence(seconds: 7)   // nothing said at all: give up after 7 s
    }

    /// stop after a pause in speech: end the audio so the recognizer sends its final result
    private func armSilence(seconds: Double) {
        silence?.invalidate()
        silence = Timer.scheduledTimer(withTimeInterval: seconds, repeats: false) { [weak self] _ in self?.finishListening() }
    }

    private func finishListening() {
        silence?.invalidate(); silence = nil
        guard request != nil else { return }
        if !heardSomething {
            task?.cancel(); stopEngine()
            emit(["type": "error", "msg": "I didn't catch anything. Tap and talk, then say your question."])
            return
        }
        request?.endAudio()
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) { [weak self] in self?.stopEngine() }
    }

    private func stopListeningNow() {
        if request != nil { task?.cancel(); stopEngine() }
    }

    private func stopEngine() {
        silence?.invalidate(); silence = nil
        if engine.isRunning { engine.stop(); engine.inputNode.removeTap(onBus: 0) }
        guard request != nil else { return }
        request = nil; task = nil
        emit(["type": "listening", "on": false])
        try? AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)
    }

    // MARK: Open questions (Apple's on-phone model, when the iPhone has it)

    func think(_ body: [String: Any]) {
        let q = body["q"] as? String ?? ""
        let facts = body["context"] as? String ?? ""
        #if canImport(FoundationModels)
        if #available(iOS 26.0, *), case .available = SystemLanguageModel.default.availability {
            Task {
                do {
                    let session = LanguageModelSession(instructions: """
                    You are Snowy, a cheerful ski guide inside a ski trip app. Answer out loud in one or two short sentences. \
                    Use only these facts about today; if they don't answer the question, say so and suggest what you can help with.
                    \(facts)
                    """)
                    let r = try await session.respond(to: q)
                    await MainActor.run { self.emit(["type": "thought", "text": r.content]) }
                } catch {
                    await MainActor.run { self.emit(["type": "thought"]) }
                }
            }
            return
        }
        #endif
        emit(["type": "thought"])
    }

    // MARK: Morning notification

    func schedule(_ body: [String: Any]) {
        let center = UNUserNotificationCenter.current()
        center.removePendingNotificationRequests(withIdentifiers: (0..<21).map { "brief-\($0)" })
        guard body["on"] as? Bool ?? true, let dates = body["dates"] as? [[Int]], !dates.isEmpty else { return }
        let hm = (body["time"] as? String ?? "08:30").split(separator: ":").compactMap { Int($0) }
        let hour = hm.first ?? 8, minute = hm.count > 1 ? hm[1] : 30
        let title = body["title"] as? String ?? "Your morning brief is ready"
        let text = body["body"] as? String ?? "Tap to listen."
        center.requestAuthorization(options: [.alert, .sound]) { ok, _ in
            guard ok else { return }
            for (i, d) in dates.prefix(21).enumerated() where d.count == 3 {
                var c = DateComponents(); c.year = d[0]; c.month = d[1]; c.day = d[2]; c.hour = hour; c.minute = minute
                let content = UNMutableNotificationContent()
                content.title = title; content.body = text; content.sound = .default
                content.userInfo = ["brief": true]
                center.add(UNNotificationRequest(identifier: "brief-\(i)", content: content,
                                                 trigger: UNCalendarNotificationTrigger(dateMatching: c, repeats: false)))
            }
            print("[app] morning brief scheduled for \(min(dates.count, 21)) day(s) at \(hour):\(String(format: "%02d", minute))")
        }
    }

    func userNotificationCenter(_ c: UNUserNotificationCenter, willPresent n: UNNotification,
                                withCompletionHandler done: @escaping (UNNotificationPresentationOptions) -> Void) {
        done([.banner, .sound])
    }

    func userNotificationCenter(_ c: UNUserNotificationCenter, didReceive r: UNNotificationResponse,
                                withCompletionHandler done: @escaping () -> Void) {
        if r.notification.request.content.userInfo["brief"] as? Bool == true {
            DispatchQueue.main.async {
                if WebBridge.shared.pageReady { WebBridge.shared.send(event: "openBrief") } else { self.pendingBrief = true }
            }
        }
        done()
    }
}
