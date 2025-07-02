import SwiftUI

struct StylePickerView: View {
    @Binding var selectedStyle: ChatStyle
    let isEnabled: Bool
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Style:")
                    .font(.headline)
                    .foregroundColor(.white)
                
                Spacer()
                
                if !isEnabled {
                    Text("Premium")
                        .font(.caption)
                        .fontWeight(.medium)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.yellow.opacity(0.2))
                        .foregroundColor(.yellow)
                        .cornerRadius(8)
                }
            }
            
            HStack(spacing: 8) {
                ForEach(ChatStyle.allCases, id: \.self) { style in
                    StyleButton(
                        style: style,
                        isSelected: selectedStyle == style,
                        isEnabled: isEnabled || style == .safe,
                        action: {
                            if isEnabled || style == .safe {
                                selectedStyle = style
                            }
                        }
                    )
                }
            }
        }
    }
}

private struct StyleButton: View {
    let style: ChatStyle
    let isSelected: Bool
    let isEnabled: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 6) {
                Text(style.emoji)
                    .font(.title2)
                
                Text(style.name)
                    .font(.caption)
                    .fontWeight(.medium)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
            .background(backgroundColor)
            .foregroundColor(foregroundColor)
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(borderColor, lineWidth: isSelected ? 2 : 1)
            )
            .scaleEffect(isSelected ? 1.05 : 1.0)
            .animation(.easeInOut(duration: 0.2), value: isSelected)
        }
        .disabled(!isEnabled)
        .opacity(isEnabled ? 1.0 : 0.6)
    }
    
    private var backgroundColor: Color {
        if isSelected {
            return style.color.opacity(0.3)
        } else {
            return Color.gray.opacity(0.1)
        }
    }
    
    private var foregroundColor: Color {
        if isSelected {
            return .white
        } else {
            return isEnabled ? .white : .gray
        }
    }
    
    private var borderColor: Color {
        if isSelected {
            return style.color
        } else {
            return Color.gray.opacity(0.3)
        }
    }
}

extension ChatStyle {
    var emoji: String {
        switch self {
        case .safe:
            return "😊"
        case .spicy:
            return "🌶️"
        case .funny:
            return "😂"
        }
    }
    
    var name: String {
        switch self {
        case .safe:
            return "Safe"
        case .spicy:
            return "Spicy"
        case .funny:
            return "Funny"
        }
    }
    
    var color: Color {
        switch self {
        case .safe:
            return .green
        case .spicy:
            return .red
        case .funny:
            return .orange
        }
    }
    
    var description: String {
        switch self {
        case .safe:
            return "Friendly and respectful"
        case .spicy:
            return "Confident and flirtatious"
        case .funny:
            return "Humorous and entertaining"
        }
    }
}

struct StylePickerView_Previews: PreviewProvider {
    static var previews: some View {
        VStack(spacing: 30) {
            // Free user (only safe available)
            StylePickerView(
                selectedStyle: .constant(.safe),
                isEnabled: false
            )
            
            // Premium user (all styles available)
            StylePickerView(
                selectedStyle: .constant(.spicy),
                isEnabled: true
            )
        }
        .padding()
        .background(Color.black)
        .preferredColorScheme(.dark)
    }
}