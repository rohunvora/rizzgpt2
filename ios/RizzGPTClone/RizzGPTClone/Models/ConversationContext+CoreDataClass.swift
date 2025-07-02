import Foundation
import CoreData

@objc(ConversationContext)
public class ConversationContext: NSManagedObject {
    
    // MARK: - Convenience Properties
    
    var suggestionCount: Int {
        return suggestions?.count ?? 0
    }
    
    var favoriteCount: Int {
        guard let suggestions = suggestions as? Set<Suggestion> else { return 0 }
        return suggestions.filter { $0.isFavorite }.count
    }
    
    var displayText: String {
        guard let sourceText = sourceText else { return "Unknown" }
        let maxLength = 100
        if sourceText.count <= maxLength {
            return sourceText
        }
        return String(sourceText.prefix(maxLength)) + "..."
    }
    
    var typeDisplayName: String {
        switch type {
        case "bio":
            return "Profile Bio"
        case "chat":
            return "Chat Reply"
        default:
            return "Unknown"
        }
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
    }
    
    // MARK: - Helper Methods
    
    func addSuggestion(_ suggestion: Suggestion) {
        suggestion.context = self
    }
    
    func removeSuggestion(_ suggestion: Suggestion) {
        suggestion.context = nil
    }
    
    var sortedSuggestions: [Suggestion] {
        guard let suggestions = suggestions as? Set<Suggestion> else { return [] }
        return suggestions.sorted { ($0.createdAt ?? Date.distantPast) < ($1.createdAt ?? Date.distantPast) }
    }
}

// MARK: - Core Data Generated accessors for suggestions
extension ConversationContext {

    @objc(addSuggestionsObject:)
    @NSManaged public func addToSuggestions(_ value: Suggestion)

    @objc(removeSuggestionsObject:)
    @NSManaged public func removeFromSuggestions(_ value: Suggestion)

    @objc(addSuggestions:)
    @NSManaged public func addToSuggestions(_ values: NSSet)

    @objc(removeSuggestions:)
    @NSManaged public func removeFromSuggestions(_ values: NSSet)
}