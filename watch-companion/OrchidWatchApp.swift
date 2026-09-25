import SwiftUI
import WatchConnectivity

@main
struct OrchidWatchApp: App {
    @StateObject private var bridge = WatchBridge.shared
    var body: some Scene {
        WindowGroup { StoryView().environmentObject(bridge) }
    }
}

final class WatchBridge: NSObject, ObservableObject, WCSessionDelegate {
    static let shared = WatchBridge()
    @Published var speaker = ""
    @Published var dialogue = "Open ProjectOrchid on iPhone."
    @Published var choices: [String] = []
    @Published var connected = false

    override init() {
        super.init()
        if WCSession.isSupported() {
            WCSession.default.delegate = self
            WCSession.default.activate()
        }
    }

    func command(_ name: String, index: Int? = nil) {
        var m: [String: Any] = ["command": name]
        if let index { m["index"] = index }
        let s = WCSession.default
        if s.isReachable { s.sendMessage(m, replyHandler: nil, errorHandler: nil) }
        else { try? s.updateApplicationContext(m) }
    }

    func session(_ session: WCSession, activationDidCompleteWith activationState: WCSessionActivationState, error: Error?) {
        DispatchQueue.main.async { self.connected = activationState == .activated }
    }

    func session(_ session: WCSession, didReceiveMessage message: [String : Any]) { apply(message) }
    func session(_ session: WCSession, didReceiveApplicationContext applicationContext: [String : Any]) { apply(applicationContext) }

    private func apply(_ m: [String: Any]) {
        DispatchQueue.main.async {
            if let v = m["speaker"] as? String { self.speaker = v }
            if let v = m["dialogue"] as? String { self.dialogue = v }
            if let v = m["choices"] as? [String] { self.choices = v }
        }
    }
}

struct StoryView: View {
    @EnvironmentObject var bridge: WatchBridge
    @State private var crown = 0.0
    @State private var lastStep = 0

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 5) {
                if !bridge.speaker.isEmpty {
                    Text(bridge.speaker).font(.headline).lineLimit(1)
                }
                Text(bridge.dialogue).font(.body).fixedSize(horizontal: false, vertical: true)

                ForEach(Array(bridge.choices.enumerated()), id: \.offset) { i, choice in
                    Button(choice) { bridge.command("choice", index: i) }
                        .font(.footnote)
                }

                if bridge.choices.isEmpty {
                    Text("Crown: back / forward").font(.caption2).opacity(0.65)
                }
            }.padding(.horizontal, 5)
        }
        .focusable(true)
        .digitalCrownRotation($crown, from: -1000, through: 1000, by: 1, sensitivity: .low, isContinuous: true, isHapticFeedbackEnabled: true)
        .onChange(of: crown) { value in
            let step = Int(value.rounded())
            guard step != lastStep else { return }
            bridge.command(step > lastStep ? "forward" : "back")
            lastStep = step
        }
    }
}
