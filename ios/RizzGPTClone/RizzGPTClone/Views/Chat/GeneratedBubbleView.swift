import SwiftUI

struct GeneratedBubbleView: View {
    let suggestion: GeneratedSuggestion
    let onCopy: () -> Void
    let onFavorite: () -> Void
    
    @State private var showingCopiedFeedback = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Header with style indicator
            HStack {
                Text(suggestion.style.emoji)
                    .font(.caption)
                
                Text(suggestion.style.name)
                    .font(.caption)
                    .fontWeight(.medium)
                    .foregroundColor(suggestion.style.color)
                
                Spacer()
                
                // Action buttons
                HStack(spacing: 16) {
                    // Favorite button
                    Button(action: {
                        onFavorite()
                        hapticFeedback()
                    }) {
                        Image(systemName: suggestion.isFavorite ? "heart.fill" : "heart")
                            .foregroundColor(suggestion.isFavorite ? .red : .gray)
                            .font(.system(size: 16))
                    }
                    
                    // Copy button
                    Button(action: {
                        copyToClipboard()
                        hapticFeedback()
                    }) {
                        Image(systemName: showingCopiedFeedback ? "checkmark" : "doc.on.doc")
                            .foregroundColor(showingCopiedFeedback ? .green : .blue)
                            .font(.system(size: 16))
                    }
                }
            }
            
            // Suggestion text
            Text(suggestion.text)
                .font(.body)
                .foregroundColor(.white)
                .fixedSize(horizontal: false, vertical: true)
                .lineLimit(nil)
            
            // Timestamp
            HStack {
                Spacer()
                Text("Just now")
                    .font(.caption2)
                    .foregroundColor(.gray)
            }
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.gray.opacity(0.1))
                .overlay(
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(suggestion.style.color.opacity(0.3), lineWidth: 1)
                )
        )
        .scaleEffect(showingCopiedFeedback ? 1.02 : 1.0)
        .animation(.easeInOut(duration: 0.2), value: showingCopiedFeedback)
    }
    
    private func copyToClipboard() {
        UIPasteboard.general.string = suggestion.text
        onCopy()
        
        // Show feedback
        showingCopiedFeedback = true
        
        // Hide feedback after delay
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
            showingCopiedFeedback = false
        }
    }
    
    private func hapticFeedback() {
        let impactFeedback = UIImpactFeedbackGenerator(style: .light)
        impactFeedback.impactOccurred()
    }
}

struct GeneratedSuggestion: Identifiable, Equatable {
    let id = UUID()
    let text: String
    let style: ChatStyle
    var isFavorite: Bool
    let timestamp: Date
    
    init(text: String, style: ChatStyle, isFavorite: Bool = false) {
        self.text = text
        self.style = style
        self.isFavorite = isFavorite
        self.timestamp = Date()
    }
}

struct SuggestionListView: View {
    let suggestions: [GeneratedSuggestion]
    let onCopy: (GeneratedSuggestion) -> Void
    let onFavorite: (GeneratedSuggestion) -> Void
    
    var body: some View {
        LazyVStack(spacing: 12) {
            ForEach(suggestions) { suggestion in
                GeneratedBubbleView(
                    suggestion: suggestion,
                    onCopy: {
                        onCopy(suggestion)
                    },
                    onFavorite: {
                        onFavorite(suggestion)
                    }
                )
            }
        }
    }
}

struct LoadingBubbleView: View {
    @State private var animationOffset: CGFloat = -100
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "sparkles")
                    .foregroundColor(.pink)
                    .font(.caption)
                
                Text("Generating...")
                    .font(.caption)
                    .fontWeight(.medium)
                    .foregroundColor(.pink)
                
                Spacer()
            }
            
            // Animated loading dots
            HStack(spacing: 8) {
                ForEach(0..<3) { index in
                    Circle()
                        .fill(Color.gray)
                        .frame(width: 8, height: 8)
                        .scaleEffect(animationOffset == CGFloat(index * 20) ? 1.2 : 0.8)
                        .animation(
                            Animation.easeInOut(duration: 0.6)
                                .repeatForever()
                                .delay(Double(index) * 0.2),
                            value: animationOffset
                        )
                }
                
                Spacer()
            }
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.gray.opacity(0.1))
                .overlay(
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(Color.pink.opacity(0.3), lineWidth: 1)
                )
        )
        .onAppear {
            animationOffset = 0
        }
    }
}

struct GeneratedBubbleView_Previews: PreviewProvider {
    static var previews: some View {
        VStack(spacing: 16) {
            GeneratedBubbleView(
                suggestion: GeneratedSuggestion(
                    text: "I see you love adventures - what's the most spontaneous trip you've ever taken?",
                    style: .safe
                ),
                onCopy: {},
                onFavorite: {}
            )
            
            GeneratedBubbleView(
                suggestion: GeneratedSuggestion(
                    text: "That hiking photo is incredible! 🌶️ I bet you have some amazing stories from the trail...",
                    style: .spicy,
                    isFavorite: true
                ),
                onCopy: {},
                onFavorite: {}
            )
            
            LoadingBubbleView()
        }
        .padding()
        .background(Color.black)
        .preferredColorScheme(.dark)
    }
}