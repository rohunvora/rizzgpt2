import XCTest
import CoreData
@testable import RizzGPTClone

final class CoreDataTests: XCTestCase {
    
    var coreDataManager: CoreDataManager!
    var testPersistenceController: PersistenceController!
    
    override func setUpWithError() throws {
        // Create in-memory persistence controller for testing
        testPersistenceController = PersistenceController(inMemory: true)
        coreDataManager = CoreDataManager(persistenceController: testPersistenceController)
    }
    
    override func tearDownWithError() throws {
        coreDataManager = nil
        testPersistenceController = nil
    }
    
    // MARK: - ConversationContext Tests
    
    func testCreateConversationContext() throws {
        let context = coreDataManager.createConversationContext(
            type: "bio",
            sourceText: "I love hiking and photography"
        )
        
        XCTAssertNotNil(context.id)
        XCTAssertEqual(context.type, "bio")
        XCTAssertEqual(context.sourceText, "I love hiking and photography")
        XCTAssertNotNil(context.createdAt)
    }
    
    func testFetchConversationContexts() throws {
        // Create test contexts
        let context1 = coreDataManager.createConversationContext(type: "bio", sourceText: "Test 1")
        let context2 = coreDataManager.createConversationContext(type: "chat", sourceText: "Test 2")
        
        let fetchedContexts = coreDataManager.fetchConversationContexts()
        
        XCTAssertEqual(fetchedContexts.count, 2)
        // Should be sorted by creation date (newest first)
        XCTAssertEqual(fetchedContexts.first?.sourceText, "Test 2")
    }
    
    func testDeleteConversationContext() throws {
        let context = coreDataManager.createConversationContext(type: "bio", sourceText: "Test")
        
        var fetchedContexts = coreDataManager.fetchConversationContexts()
        XCTAssertEqual(fetchedContexts.count, 1)
        
        coreDataManager.deleteConversationContext(context)
        
        fetchedContexts = coreDataManager.fetchConversationContexts()
        XCTAssertEqual(fetchedContexts.count, 0)
    }
    
    // MARK: - Suggestion Tests
    
    func testCreateSuggestion() throws {
        let context = coreDataManager.createConversationContext(type: "bio", sourceText: "Test")
        let suggestion = coreDataManager.createSuggestion(
            text: "Great suggestion!",
            style: "safe",
            context: context
        )
        
        XCTAssertNotNil(suggestion.id)
        XCTAssertEqual(suggestion.text, "Great suggestion!")
        XCTAssertEqual(suggestion.style, "safe")
        XCTAssertFalse(suggestion.isFavorite)
        XCTAssertEqual(suggestion.context, context)
        XCTAssertNotNil(suggestion.createdAt)
    }
    
    func testToggleFavorite() throws {
        let context = coreDataManager.createConversationContext(type: "bio", sourceText: "Test")
        let suggestion = coreDataManager.createSuggestion(text: "Test", style: "safe", context: context)
        
        XCTAssertFalse(suggestion.isFavorite)
        
        coreDataManager.toggleFavorite(suggestion: suggestion)
        XCTAssertTrue(suggestion.isFavorite)
        
        coreDataManager.toggleFavorite(suggestion: suggestion)
        XCTAssertFalse(suggestion.isFavorite)
    }
    
    func testFetchFavoriteSuggestions() throws {
        let context = coreDataManager.createConversationContext(type: "bio", sourceText: "Test")
        let suggestion1 = coreDataManager.createSuggestion(text: "Test 1", style: "safe", context: context)
        let suggestion2 = coreDataManager.createSuggestion(text: "Test 2", style: "funny", context: context)
        
        // Mark one as favorite
        coreDataManager.toggleFavorite(suggestion: suggestion1)
        
        let favorites = coreDataManager.fetchFavoriteSuggestions()
        XCTAssertEqual(favorites.count, 1)
        XCTAssertEqual(favorites.first?.text, "Test 1")
    }
    
    func testFetchSuggestionsForContext() throws {
        let context1 = coreDataManager.createConversationContext(type: "bio", sourceText: "Test 1")
        let context2 = coreDataManager.createConversationContext(type: "chat", sourceText: "Test 2")
        
        let suggestion1 = coreDataManager.createSuggestion(text: "Suggestion 1", style: "safe", context: context1)
        let suggestion2 = coreDataManager.createSuggestion(text: "Suggestion 2", style: "funny", context: context1)
        let suggestion3 = coreDataManager.createSuggestion(text: "Suggestion 3", style: "spicy", context: context2)
        
        let context1Suggestions = coreDataManager.fetchSuggestions(for: context1)
        XCTAssertEqual(context1Suggestions.count, 2)
        
        let context2Suggestions = coreDataManager.fetchSuggestions(for: context2)
        XCTAssertEqual(context2Suggestions.count, 1)
        XCTAssertEqual(context2Suggestions.first?.text, "Suggestion 3")
    }
    
    // MARK: - Bulk Operations Tests
    
    func testClearAllData() throws {
        let context = coreDataManager.createConversationContext(type: "bio", sourceText: "Test")
        let suggestion = coreDataManager.createSuggestion(text: "Test", style: "safe", context: context)
        
        var contexts = coreDataManager.fetchConversationContexts()
        var favorites = coreDataManager.fetchFavoriteSuggestions()
        XCTAssertEqual(contexts.count, 1)
        
        coreDataManager.clearAllData()
        
        contexts = coreDataManager.fetchConversationContexts()
        favorites = coreDataManager.fetchFavoriteSuggestions()
        XCTAssertEqual(contexts.count, 0)
        XCTAssertEqual(favorites.count, 0)
    }
    
    func testGetStatistics() throws {
        let context1 = coreDataManager.createConversationContext(type: "bio", sourceText: "Test 1")
        let context2 = coreDataManager.createConversationContext(type: "chat", sourceText: "Test 2")
        
        let suggestion1 = coreDataManager.createSuggestion(text: "Test 1", style: "safe", context: context1)
        let suggestion2 = coreDataManager.createSuggestion(text: "Test 2", style: "funny", context: context1)
        let suggestion3 = coreDataManager.createSuggestion(text: "Test 3", style: "spicy", context: context2)
        
        // Mark one as favorite
        coreDataManager.toggleFavorite(suggestion: suggestion1)
        
        let stats = coreDataManager.getStatistics()
        XCTAssertEqual(stats.totalContexts, 2)
        XCTAssertEqual(stats.totalSuggestions, 3)
        XCTAssertEqual(stats.favoriteCount, 1)
    }
    
    // MARK: - Model Extension Tests
    
    func testConversationContextDisplayProperties() throws {
        let context = coreDataManager.createConversationContext(
            type: "bio",
            sourceText: "This is a very long text that should be truncated when displayed in the UI because it exceeds the maximum length"
        )
        
        XCTAssertEqual(context.typeDisplayName, "Profile Bio")
        XCTAssertTrue(context.displayText.hasSuffix("..."))
        XCTAssertLessThan(context.displayText.count, 105) // 100 + "..."
    }
    
    func testSuggestionDisplayProperties() throws {
        let context = coreDataManager.createConversationContext(type: "bio", sourceText: "Test")
        let suggestion = coreDataManager.createSuggestion(text: "Test suggestion", style: "spicy", context: context)
        
        XCTAssertEqual(suggestion.styleDisplayName, "Spicy")
        XCTAssertEqual(suggestion.styleEmoji, "🌶️")
        XCTAssertEqual(suggestion.favoriteIcon, "heart")
        XCTAssertEqual(suggestion.favoriteColor, "gray")
        
        suggestion.toggleFavorite()
        XCTAssertEqual(suggestion.favoriteIcon, "heart.fill")
        XCTAssertEqual(suggestion.favoriteColor, "red")
    }
    
    func testSuggestionValidation() throws {
        let context = coreDataManager.createConversationContext(type: "bio", sourceText: "Test")
        let validSuggestion = coreDataManager.createSuggestion(text: "Valid text", style: "safe", context: context)
        
        XCTAssertTrue(validSuggestion.isValid)
        
        // Test invalid suggestion (empty text)
        let invalidSuggestion = Suggestion(context: coreDataManager.viewContext)
        invalidSuggestion.text = ""
        invalidSuggestion.style = "safe"
        
        XCTAssertFalse(invalidSuggestion.isValid)
    }
}