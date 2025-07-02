import Foundation
import CoreData

@objc(Suggestion)
public class Suggestion: NSManagedObject {
    
    // MARK: - Convenience Properties
    
    var displayText: String {
        return text ?? "Unknown suggestion"
    }
    
    var styleDisplayName: String {
        switch style {
        case "safe":
            return "Safe"
        case "spicy":
            return "Spicy"
        case "funny":
            return "Funny"
        default:
            return "Unknown"
        }
    }
    
    var styleEmoji: String {
        switch style {
        case "safe":
            return "😊"
        case "spicy":
            return "🌶️"
        case "funny":
            return "😂"
        default:
            return "💬"
        }
    }
    
    var favoriteIcon: String {
        return isFavorite ? "heart.fill" : "heart"
    }
    
    var favoriteColor: String {
        return isFavorite ? "red" : "gray"
    }
    
    var contextTypeDisplayName: String {
        return context?.typeDisplayName ?? "Unknown"
    }
    
    // MARK: - Core Data Lifecycle
    
    public override func awakeFromInsert() {
        super.awakeFromInsert()
        
        if id == nil {
            id = UUID()
        }
        
        if createdAt == nil {
            createdAt = Date()
        }
        
        // Default to not favorite
        isFavorite = false
    }
    
    // MARK: - Helper Methods
    
    func toggleFavorite() {
        isFavorite.toggle()
    }
    
    var formattedCreatedAt: String {
        guard let createdAt = createdAt else { return "Unknown" }
        
        let formatter = DateFormatter()
        let calendar = Calendar.current
        
        if calendar.isDateInToday(createdAt) {
            formatter.dateFormat = "h:mm a"
            return "Today at \(formatter.string(from: createdAt))"
        } else if calendar.isDateInYesterday(createdAt) {
            formatter.dateFormat = "h:mm a"
            return "Yesterday at \(formatter.string(from: createdAt))"
        } else if calendar.dateInterval(of: .weekOfYear, for: Date())?.contains(createdAt) == true {
            formatter.dateFormat = "EEEE"
            return formatter.string(from: createdAt)
        } else {
            formatter.dateFormat = "MMM d"
            return formatter.string(from: createdAt)
        }
    }
    
    var isRecent: Bool {
        guard let createdAt = createdAt else { return false }
        let hoursSinceCreation = Date().timeIntervalSince(createdAt) / 3600
        return hoursSinceCreation < 24
    }
    
    // MARK: - Validation
    
    var isValid: Bool {
        guard let text = text, !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            return false
        }
        
        guard let style = style, ["safe", "spicy", "funny"].contains(style) else {
            return false
        }
        
        return true
    }
}