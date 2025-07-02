import SwiftUI

struct SettingsView: View {
    @State private var showingClearDataAlert = false
    @State private var showingPrivacyPolicy = false
    @State private var showingTermsOfUse = false
    
    var body: some View {
        NavigationView {
            List {
                // App Info Section
                Section {
                    HStack {
                        Image(systemName: "heart.circle.fill")
                            .font(.largeTitle)
                            .foregroundColor(.pink)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text("RizzGPT Clone")
                                .font(.headline)
                                .foregroundColor(.white)
                            
                            Text("Version 1.0")
                                .font(.caption)
                                .foregroundColor(.gray)
                        }
                        
                        Spacer()
                    }
                    .padding(.vertical, 8)
                } header: {
                    Text("App Information")
                }
                .listRowBackground(Color.gray.opacity(0.1))
                
                // Privacy Section
                Section {
                    Button(action: {
                        showingClearDataAlert = true
                    }) {
                        HStack {
                            Image(systemName: "trash")
                                .foregroundColor(.red)
                            Text("Clear History")
                                .foregroundColor(.white)
                            Spacer()
                        }
                    }
                    
                    HStack {
                        Image(systemName: "shield.checkered")
                            .foregroundColor(.green)
                        Text("Data stays on device")
                            .foregroundColor(.white)
                        Spacer()
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundColor(.green)
                    }
                } header: {
                    Text("Privacy")
                } footer: {
                    Text("Your conversations and favorites are stored locally on your device and never shared with third parties.")
                }
                .listRowBackground(Color.gray.opacity(0.1))
                
                // Legal Section
                Section {
                    Button(action: {
                        showingPrivacyPolicy = true
                    }) {
                        HStack {
                            Image(systemName: "hand.raised")
                                .foregroundColor(.blue)
                            Text("Privacy Policy")
                                .foregroundColor(.white)
                            Spacer()
                            Image(systemName: "chevron.right")
                                .foregroundColor(.gray)
                                .font(.caption)
                        }
                    }
                    
                    Button(action: {
                        showingTermsOfUse = true
                    }) {
                        HStack {
                            Image(systemName: "doc.text")
                                .foregroundColor(.blue)
                            Text("Terms of Use")
                                .foregroundColor(.white)
                            Spacer()
                            Image(systemName: "chevron.right")
                                .foregroundColor(.gray)
                                .font(.caption)
                        }
                    }
                } header: {
                    Text("Legal")
                }
                .listRowBackground(Color.gray.opacity(0.1))
                
                // About Section
                Section {
                    HStack {
                        Image(systemName: "info.circle")
                            .foregroundColor(.blue)
                        Text("Build")
                            .foregroundColor(.white)
                        Spacer()
                        Text("1.0.0 (1)")
                            .foregroundColor(.gray)
                            .font(.caption)
                    }
                    
                    HStack {
                        Image(systemName: "calendar")
                            .foregroundColor(.blue)
                        Text("Release Date")
                            .foregroundColor(.white)
                        Spacer()
                        Text("2024")
                            .foregroundColor(.gray)
                            .font(.caption)
                    }
                } header: {
                    Text("About")
                } footer: {
                    VStack(alignment: .center, spacing: 8) {
                        Text("Made with ❤️ for respectful dating")
                            .font(.caption)
                            .foregroundColor(.gray)
                            .multilineTextAlignment(.center)
                        
                        Text("Please use this app responsibly and treat others with respect.")
                            .font(.caption2)
                            .foregroundColor(.gray)
                            .multilineTextAlignment(.center)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.top, 20)
                }
                .listRowBackground(Color.gray.opacity(0.1))
            }
            .listStyle(GroupedListStyle())
            .background(Color.black)
            .scrollContentBackground(.hidden)
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.large)
        }
        .alert("Clear All Data", isPresented: $showingClearDataAlert) {
            Button("Cancel", role: .cancel) { }
            Button("Clear", role: .destructive) {
                clearAllData()
            }
        } message: {
            Text("This will permanently delete all your saved conversations and favorites. This action cannot be undone.")
        }
        .sheet(isPresented: $showingPrivacyPolicy) {
            WebView(url: "https://sites.google.com/view/rizzgpt-privacy", title: "Privacy Policy")
        }
        .sheet(isPresented: $showingTermsOfUse) {
            WebView(url: "https://sites.google.com/view/rizzgpt-terms", title: "Terms of Use")
        }
    }
    
    private func clearAllData() {
        // TODO: Clear Core Data
        print("Clearing all data...")
    }
}

struct WebView: View {
    let url: String
    let title: String
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            VStack {
                // Placeholder for web content
                VStack(spacing: 20) {
                    Image(systemName: "globe")
                        .font(.system(size: 60))
                        .foregroundColor(.blue)
                    
                    Text(title)
                        .font(.title)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                    
                    Text("Web content would load here")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                    
                    Text(url)
                        .font(.caption)
                        .foregroundColor(.blue)
                        .multilineTextAlignment(.center)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(Color.black)
            }
            .navigationTitle(title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
        .preferredColorScheme(.dark)
    }
}

struct SettingsView_Previews: PreviewProvider {
    static var previews: some View {
        SettingsView()
            .preferredColorScheme(.dark)
    }
}