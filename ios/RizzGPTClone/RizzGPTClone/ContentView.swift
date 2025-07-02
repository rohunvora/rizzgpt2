import SwiftUI

struct ContentView: View {
    var body: some View {
        TabView {
            ChatView()
                .tabItem {
                    Image(systemName: "message.fill")
                    Text("Chat")
                }
            
            LibraryView()
                .tabItem {
                    Image(systemName: "heart.fill")
                    Text("Library")
                }
            
            SettingsView()
                .tabItem {
                    Image(systemName: "gear.fill")
                    Text("Settings")
                }
        }
        .preferredColorScheme(.dark)
        .accentColor(.pink)
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
            .preferredColorScheme(.dark)
    }
}