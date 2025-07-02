import SwiftUI

struct ChatView: View {
    @StateObject private var viewModel = ChatViewModel()
    @State private var isPremium = false // TODO: Connect to subscription state
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Main content area
                ScrollViewReader { proxy in
                    ScrollView {
                        LazyVStack(spacing: 16) {
                            if viewModel.suggestions.isEmpty && !viewModel.isLoading {
                                // Welcome message
                                WelcomeView()
                                    .padding(.top, 40)
                            } else {
                                // Generated suggestions
                                SuggestionListView(
                                    suggestions: viewModel.suggestions,
                                    onCopy: { suggestion in
                                        viewModel.copySuggestion(suggestion)
                                    },
                                    onFavorite: { suggestion in
                                        viewModel.toggleFavorite(for: suggestion)
                                    }
                                )
                                .padding(.horizontal)
                                
                                // Loading indicator
                                if viewModel.isLoading {
                                    LoadingBubbleView()
                                        .padding(.horizontal)
                                        .id("loading")
                                }
                            }
                        }
                    }
                    .onChange(of: viewModel.isLoading) { isLoading in
                        if isLoading {
                            withAnimation(.easeInOut(duration: 0.5)) {
                                proxy.scrollTo("loading", anchor: .bottom)
                            }
                        }
                    }
                }
                
                // Input section
                VStack(spacing: 16) {
                    // Style picker
                    StylePickerView(
                        selectedStyle: $viewModel.selectedStyle,
                        isEnabled: isPremium
                    )
                    .padding(.horizontal)
                    
                    // Text input
                    ChatInputView(
                        text: $viewModel.inputText,
                        placeholder: "Paste bio or chat messages here...",
                        onSubmit: {
                            // Handle return key if needed
                        }
                    )
                    .padding(.horizontal)
                    
                    // Action buttons
                    HStack(spacing: 12) {
                        ActionButton(
                            title: "Ice-breaker",
                            icon: "sparkles",
                            color: .pink,
                            isEnabled: viewModel.canGenerate && !viewModel.isInputTooLong,
                            action: {
                                viewModel.generateIcebreaker()
                            }
                        )
                        
                        ActionButton(
                            title: "Reply",
                            icon: "arrow.turn.up.right",
                            color: .blue,
                            isEnabled: viewModel.canGenerate && !viewModel.isInputTooLong,
                            action: {
                                viewModel.generateReply()
                            }
                        )
                    }
                    .padding(.horizontal)
                }
                .padding(.bottom)
                .background(Color.black)
            }
            .background(Color.black)
            .navigationTitle("Chat")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    if !viewModel.suggestions.isEmpty {
                        Button("Clear") {
                            viewModel.clearSuggestions()
                        }
                        .foregroundColor(.gray)
                    }
                }
            }
        }
        .alert("Error", isPresented: $viewModel.showingError) {
            Button("OK") {
                viewModel.showingError = false
            }
        } message: {
            if let errorMessage = viewModel.errorMessage {
                Text(errorMessage)
            }
        }
    }
}

private struct WelcomeView: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "heart.circle.fill")
                .font(.system(size: 60))
                .foregroundColor(.pink)
            
            Text("RizzGPT Clone")
                .font(.title)
                .fontWeight(.bold)
                .foregroundColor(.white)
            
            Text("Paste a bio or chat to get AI-powered suggestions")
                .font(.subheadline)
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
            
            VStack(spacing: 12) {
                FeatureRow(icon: "sparkles", text: "Generate ice-breakers from dating profiles")
                FeatureRow(icon: "arrow.turn.up.right", text: "Get reply suggestions for ongoing chats")
                FeatureRow(icon: "heart", text: "Save your favorites for later")
            }
            .padding(.top, 20)
        }
        .frame(maxWidth: .infinity)
    }
}

private struct FeatureRow: View {
    let icon: String
    let text: String
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .foregroundColor(.pink)
                .font(.system(size: 16))
                .frame(width: 20)
            
            Text(text)
                .font(.subheadline)
                .foregroundColor(.gray)
            
            Spacer()
        }
        .padding(.horizontal, 40)
    }
}

private struct ActionButton: View {
    let title: String
    let icon: String
    let color: Color
    let isEnabled: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack {
                Image(systemName: icon)
                Text(title)
            }
            .font(.headline)
            .foregroundColor(.white)
            .frame(maxWidth: .infinity)
            .padding()
            .background(isEnabled ? color : Color.gray)
            .cornerRadius(12)
        }
        .disabled(!isEnabled)
        .opacity(isEnabled ? 1.0 : 0.6)
    }
}

struct ChatView_Previews: PreviewProvider {
    static var previews: some View {
        ChatView()
            .preferredColorScheme(.dark)
    }
}