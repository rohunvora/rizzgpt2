import CoreData
import Foundation

@MainActor
class CoreDataManager: ObservableObject {
    private let persistenceController: PersistenceController
    
    var viewContext: NSManagedObjectContext {
        persistenceController.container.viewContext
    }
    
    init(persistenceController: PersistenceController = .shared) {
        self.persistenceController = persistenceController
    }
    
    // MARK: - ConversationContext Operations
    
    func createConversationContext(type: String, sourceText: String) -> ConversationContext {
        let context = ConversationContext(context: viewContext)
        context.id = UUID()
        context.type = type
        context.sourceText = sourceText
        context.createdAt = Date()
        
        save()
        return context
    }
    
    func fetchConversationContexts() -> [ConversationContext] {
        let request: NSFetchRequest<ConversationContext> = ConversationContext.fetchRequest()
        request.sortDescriptors = [NSSortDescriptor(keyPath: \ConversationContext.createdAt, ascending: false)]
        
        do {
            return try viewContext.fetch(request)
        } catch {
            print("Failed to fetch conversation contexts: \(error)")
            return []
        }
    }
    
    func deleteConversationContext(_ context: ConversationContext) {
        viewContext.delete(context)
        save()
    }
    
    // MARK: - Suggestion Operations
    
    func createSuggestion(text: String, style: String, context: ConversationContext) -> Suggestion {
        let suggestion = Suggestion(context: viewContext)
        suggestion.id = UUID()
        suggestion.text = text
        suggestion.style = style
        suggestion.isFavorite = false
        suggestion.createdAt = Date()
        suggestion.context = context
        
        save()
        return suggestion
    }
    
    func fetchFavoriteSuggestions() -> [Suggestion] {
        let request: NSFetchRequest<Suggestion> = Suggestion.fetchRequest()
        request.predicate = NSPredicate(format: "isFavorite == YES")
        request.sortDescriptors = [NSSortDescriptor(keyPath: \Suggestion.createdAt, ascending: false)]
        
        do {
            return try viewContext.fetch(request)
        } catch {
            print("Failed to fetch favorite suggestions: \(error)")
            return []
        }
    }
    
    func fetchSuggestions(for context: ConversationContext) -> [Suggestion] {
        let request: NSFetchRequest<Suggestion> = Suggestion.fetchRequest()
        request.predicate = NSPredicate(format: "context == %@", context)
        request.sortDescriptors = [NSSortDescriptor(keyPath: \Suggestion.createdAt, ascending: true)]
        
        do {
            return try viewContext.fetch(request)
        } catch {
            print("Failed to fetch suggestions for context: \(error)")
            return []
        }
    }
    
    func toggleFavorite(suggestion: Suggestion) {
        suggestion.isFavorite.toggle()
        save()
    }
    
    func deleteSuggestion(_ suggestion: Suggestion) {
        viewContext.delete(suggestion)
        save()
    }
    
    // MARK: - Bulk Operations
    
    func clearAllData() {
        // Delete all suggestions first (due to relationship)
        let suggestionRequest: NSFetchRequest<NSFetchRequestResult> = Suggestion.fetchRequest()
        let deleteSuggestionsRequest = NSBatchDeleteRequest(fetchRequest: suggestionRequest)
        
        let contextRequest: NSFetchRequest<NSFetchRequestResult> = ConversationContext.fetchRequest()
        let deleteContextsRequest = NSBatchDeleteRequest(fetchRequest: contextRequest)
        
        do {
            try viewContext.execute(deleteSuggestionsRequest)
            try viewContext.execute(deleteContextsRequest)
            save()
        } catch {
            print("Failed to clear all data: \(error)")
        }
    }
    
    func exportFavorites() -> [String] {
        let favorites = fetchFavoriteSuggestions()
        return favorites.compactMap { $0.text }
    }
    
    // MARK: - Statistics
    
    func getStatistics() -> (totalContexts: Int, totalSuggestions: Int, favoriteCount: Int) {
        let contextCount = fetchConversationContexts().count
        
        let allSuggestionsRequest: NSFetchRequest<Suggestion> = Suggestion.fetchRequest()
        let allSuggestionsCount = (try? viewContext.count(for: allSuggestionsRequest)) ?? 0
        
        let favoriteCount = fetchFavoriteSuggestions().count
        
        return (contextCount, allSuggestionsCount, favoriteCount)
    }
    
    // MARK: - Private Methods
    
    private func save() {
        persistenceController.save()
    }
}