import SwiftUI

struct ChatInputView: View {
    @Binding var text: String
    let placeholder: String
    let onSubmit: () -> Void
    
    @FocusState private var isTextFieldFocused: Bool
    @State private var textHeight: CGFloat = 80
    
    private let minHeight: CGFloat = 80
    private let maxHeight: CGFloat = 150
    
    var body: some View {
        VStack(spacing: 0) {
            // Text input area
            ZStack(alignment: .topLeading) {
                // Background
                RoundedRectangle(cornerRadius: 16)
                    .fill(Color.gray.opacity(0.1))
                    .overlay(
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(isTextFieldFocused ? Color.pink : Color.gray.opacity(0.3), lineWidth: 1)
                    )
                
                // Text editor
                TextEditor(text: $text)
                    .padding(16)
                    .background(Color.clear)
                    .foregroundColor(.white)
                    .font(.body)
                    .focused($isTextFieldFocused)
                    .scrollContentBackground(.hidden)
                    .frame(minHeight: minHeight, maxHeight: maxHeight)
                    .onChange(of: text) { _ in
                        updateTextHeight()
                    }
                
                // Placeholder text
                if text.isEmpty {
                    Text(placeholder)
                        .foregroundColor(.gray)
                        .font(.body)
                        .padding(.horizontal, 20)
                        .padding(.vertical, 24)
                        .allowsHitTesting(false)
                }
                
                // Character count
                VStack {
                    Spacer()
                    HStack {
                        Spacer()
                        Text("\(text.count)/1500")
                            .font(.caption2)
                            .foregroundColor(text.count > 1400 ? .red : .gray)
                            .padding(.trailing, 8)
                            .padding(.bottom, 8)
                    }
                }
            }
            .frame(height: textHeight)
            .animation(.easeInOut(duration: 0.2), value: textHeight)
        }
    }
    
    private func updateTextHeight() {
        // Calculate text height based on content
        let font = UIFont.preferredFont(forTextStyle: .body)
        let textWidth = UIScreen.main.bounds.width - 64 // Account for padding
        
        let textRect = text.boundingRect(
            with: CGSize(width: textWidth, height: .greatestFiniteMagnitude),
            options: [.usesLineFragmentOrigin, .usesFontLeading],
            attributes: [.font: font],
            context: nil
        )
        
        let calculatedHeight = max(minHeight, min(maxHeight, textRect.height + 48))
        
        if abs(calculatedHeight - textHeight) > 1 {
            textHeight = calculatedHeight
        }
    }
}

struct ChatInputView_Previews: PreviewProvider {
    static var previews: some View {
        VStack {
            ChatInputView(
                text: .constant(""),
                placeholder: "Paste bio or chat messages here...",
                onSubmit: {}
            )
            
            ChatInputView(
                text: .constant("This is a longer text that should expand the text view to show multiple lines of content and demonstrate the dynamic height adjustment feature."),
                placeholder: "Placeholder",
                onSubmit: {}
            )
        }
        .padding()
        .background(Color.black)
        .preferredColorScheme(.dark)
    }
}