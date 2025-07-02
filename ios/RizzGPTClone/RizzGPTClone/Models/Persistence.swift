import CoreData
import Foundation

struct PersistenceController {
    static let shared = PersistenceController()
    
    static var preview: PersistenceController = {
        let result = PersistenceController(inMemory: true)
        let viewContext = result.container.viewContext
        
        // Create sample data for previews
        let sampleContext = ConversationContext(context: viewContext)
        sampleContext.id = UUID()
        sampleContext.type = "bio"
        sampleContext.sourceText = "I love hiking and photography. Always looking for new adventures!"
        sampleContext.createdAt = Date()
        
        let suggestion1 = Suggestion(context: viewContext)
        suggestion1.id = UUID()
        suggestion1.text = "I see you love adventures - what's the most spontaneous trip you've ever taken?"
        suggestion1.style = "safe"
        suggestion1.isFavorite = false
        suggestion1.createdAt = Date()
        suggestion1.context = sampleContext
        
        let suggestion2 = Suggestion(context: viewContext)
        suggestion2.id = UUID()
        suggestion2.text = "A fellow photographer! What's your favorite subject to capture?"
        suggestion2.style = "safe"
        suggestion2.isFavorite = true
        suggestion2.createdAt = Date()
        suggestion2.context = sampleContext
        
        do {
            try viewContext.save()
        } catch {
            // Replace this implementation with code to handle the error appropriately.
            let nsError = error as NSError
            fatalError("Unresolved error \(nsError), \(nsError.userInfo)")
        }
        return result
    }()
    
    let container: NSPersistentContainer
    
    init(inMemory: Bool = false) {
        container = NSPersistentContainer(name: "CoreDataModels")
        
        if inMemory {
            container.persistentStoreDescriptions.first!.url = URL(fileURLWithPath: "/dev/null")
        }
        
        // Configure store settings for better performance
        container.persistentStoreDescriptions.first?.setOption(true as NSNumber, 
                                                               forKey: NSPersistentHistoryTrackingKey)
        container.persistentStoreDescriptions.first?.setOption(true as NSNumber, 
                                                               forKey: NSPersistentStoreRemoteChangeNotificationPostOptionKey)
        
        container.loadPersistentStores(completionHandler: { (storeDescription, error) in
            if let error = error as NSError? {
                // Replace this implementation with code to handle the error appropriately.
                fatalError("Unresolved error \(error), \(error.userInfo)")
            }
        })
        
        container.viewContext.automaticallyMergesChangesFromParent = true
        container.viewContext.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy
    }
}

// MARK: - Core Data Operations
extension PersistenceController {
    
    /// Save the view context
    func save() {
        let context = container.viewContext
        
        if context.hasChanges {
            do {
                try context.save()
            } catch {
                let nsError = error as NSError
                print("Failed to save context: \(nsError), \(nsError.userInfo)")
            }
        }
    }
    
    /// Perform a background task
    func performBackgroundTask(_ block: @escaping (NSManagedObjectContext) -> Void) {
        container.performBackgroundTask(block)
    }
}