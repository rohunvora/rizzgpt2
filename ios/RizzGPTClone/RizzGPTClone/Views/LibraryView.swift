import SwiftUI

struct LibraryView: View {
    @State private var favorites: [String] = []
    @State private var searchText = ""
    
    var body: some View {
        NavigationView {
            VStack {
                if favorites.isEmpty {
                    // Empty state
                    VStack(spacing: 20) {
                        Image(systemName: "heart.slash")
                            .font(.system(size: 60))
                            .foregroundColor(.gray)
                        
                        Text("No Favorites Yet")
                            .font(.title2)
                            .fontWeight(.bold)
                            .foregroundColor(.white)
                        
                        Text("Save your best suggestions by tapping the heart icon in the Chat tab")
                            .font(.subheadline)
                            .foregroundColor(.gray)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal, 40)
                        
                        Button(action: {
                            // TODO: Navigate to Chat tab
                        }) {
                            HStack {
                                Image(systemName: "message.fill")
                                Text("Go to Chat")
                            }
                            .font(.headline)
                            .foregroundColor(.white)
                            .padding()
                            .background(Color.pink)
                            .cornerRadius(12)
                        }
                        .padding(.top, 20)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    .background(Color.black)
                } else {
                    // Favorites list
                    List {
                        ForEach(filteredFavorites, id: \.self) { favorite in
                            FavoriteRowView(text: favorite)
                        }
                        .onDelete(perform: deleteFavorites)
                    }
                    .listStyle(PlainListStyle())
                    .background(Color.black)
                    .searchable(text: $searchText, prompt: "Search favorites...")
                }
            }
            .background(Color.black)
            .navigationTitle("Library")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    if !favorites.isEmpty {
                        Button("Clear All") {
                            clearAllFavorites()
                        }
                        .foregroundColor(.red)
                    }
                }
            }
        }
        .onAppear {
            loadFavorites()
        }
    }
    
    private var filteredFavorites: [String] {
        if searchText.isEmpty {
            return favorites
        } else {
            return favorites.filter { $0.localizedCaseInsensitiveContains(searchText) }
        }
    }
    
    private func loadFavorites() {
        // TODO: Load from Core Data
        // For now, add some sample data
        favorites = [
            "I see you love adventures - what's the most spontaneous trip you've ever taken?",
            "A fellow photographer! What's your favorite subject to capture?",
            "Hiking enthusiast here too! What's your dream hiking destination?"
        ]
    }
    
    private func deleteFavorites(offsets: IndexSet) {
        favorites.remove(atOffsets: offsets)
        // TODO: Update Core Data
    }
    
    private func clearAllFavorites() {
        favorites.removeAll()
        // TODO: Clear from Core Data
    }
}

struct FavoriteRowView: View {
    let text: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: "heart.fill")
                    .foregroundColor(.red)
                    .font(.caption)
                
                Text("Favorite")
                    .font(.caption)
                    .foregroundColor(.gray)
                
                Spacer()
                
                Button(action: {
                    // TODO: Copy to clipboard
                    copyToClipboard()
                }) {
                    Image(systemName: "doc.on.doc")
                        .foregroundColor(.blue)
                }
            }
            
            Text(text)
                .font(.body)
                .foregroundColor(.white)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(.vertical, 4)
        .listRowBackground(Color.gray.opacity(0.1))
    }
    
    private func copyToClipboard() {
        UIPasteboard.general.string = text
        // TODO: Show toast confirmation
    }
}

struct LibraryView_Previews: PreviewProvider {
    static var previews: some View {
        LibraryView()
            .preferredColorScheme(.dark)
    }
}