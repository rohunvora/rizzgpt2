import SwiftUI

struct ChatView: View {
    @State private var inputText = ""
    @State private var selectedStyle: ChatStyle = .safe
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Main content area
                ScrollView {
                    VStack(spacing: 16) {
                        // Welcome message
                        VStack(spacing: 12) {
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
                        }
                        .padding(.top, 40)
                        
                        Spacer(minLength: 100)
                    }
                }
                
                // Input section
                VStack(spacing: 16) {
                    // Style picker
                    HStack(spacing: 16) {
                        Text("Style:")
                            .foregroundColor(.white)
                            .font(.headline)
                        
                        Spacer()
                        
                        ForEach(ChatStyle.allCases, id: \.self) { style in
                            Button(action: {
                                selectedStyle = style
                            }) {
                                Text(style.displayName)
                                    .font(.caption)
                                    .fontWeight(.medium)
                                    .padding(.horizontal, 12)
                                    .padding(.vertical, 6)
                                    .background(
                                        selectedStyle == style ? Color.pink : Color.gray.opacity(0.3)
                                    )
                                    .foregroundColor(.white)
                                    .cornerRadius(12)
                            }
                        }
                    }
                    .padding(.horizontal)
                    
                    // Text input
                    VStack(spacing: 12) {
                        TextEditor(text: $inputText)
                            .frame(minHeight: 80, maxHeight: 120)
                            .padding(12)
                            .background(Color.gray.opacity(0.1))
                            .cornerRadius(12)
                            .foregroundColor(.white)
                            .overlay(
                                RoundedRectangle(cornerRadius: 12)
                                    .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                            )
                            .overlay(
                                // Placeholder
                                Group {
                                    if inputText.isEmpty {
                                        Text("Paste bio or chat messages here...")
                                            .foregroundColor(.gray)
                                            .padding(16)
                                            .allowsHitTesting(false)
                                    }
                                },
                                alignment: .topLeading
                            )
                        
                        // Action buttons
                        HStack(spacing: 12) {
                            Button(action: {
                                // TODO: Generate ice-breaker
                            }) {
                                HStack {
                                    Image(systemName: "sparkles")
                                    Text("Ice-breaker")
                                }
                                .font(.headline)
                                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.pink)
                                .cornerRadius(12)
                            }
                            .disabled(inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                            
                            Button(action: {
                                // TODO: Generate reply
                            }) {
                                HStack {
                                    Image(systemName: "arrow.turn.up.right")
                                    Text("Reply")
                                }
                                .font(.headline)
                                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.blue)
                                .cornerRadius(12)
                            }
                            .disabled(inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                        }
                    }
                    .padding(.horizontal)
                }
                .padding(.bottom)
                .background(Color.black)
            }
            .background(Color.black)
            .navigationTitle("Chat")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

enum ChatStyle: String, CaseIterable {
    case safe = "safe"
    case spicy = "spicy"
    case funny = "funny"
    
    var displayName: String {
        switch self {
        case .safe:
            return "😊 Safe"
        case .spicy:
            return "🌶️ Spicy"
        case .funny:
            return "😂 Funny"
        }
    }
}

struct ChatView_Previews: PreviewProvider {
    static var previews: some View {
        ChatView()
            .preferredColorScheme(.dark)
    }
}