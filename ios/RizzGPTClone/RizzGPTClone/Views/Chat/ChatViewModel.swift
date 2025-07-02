import SwiftUI
import Combine

@MainActor
class ChatViewModel: ObservableObject {
    // MARK: - Published Properties
    @Published var inputText = ""
    @Published var selectedStyle: ChatStyle = .safe
    @Published var suggestions: [GeneratedSuggestion] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var showingError = false
    
    // MARK: - Private Properties
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Computed Properties
    var canGenerate: Bool {
        !inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && !isLoading
    }
    
    var inputCharacterCount: Int {
        inputText.count
    }
    
    var isInputTooLong: Bool {
        inputText.count > 1500
    }
    
    // MARK: - Initialization
    init() {
        setupBindings()
    }
    
    // MARK: - Public Methods
    func generateIcebreaker() {
        guard canGenerate else { return }
        
        Task {
            await performGeneration(mode: .pickup)
        }
    }
    
    func generateReply() {
        guard canGenerate else { return }
        
        Task {
            await performGeneration(mode: .reply)
        }
    }
    
    func toggleFavorite(for suggestion: GeneratedSuggestion) {
        guard let index = suggestions.firstIndex(where: { $0.id == suggestion.id }) else { return }
        
        suggestions[index].isFavorite.toggle()
        
        // TODO: Update Core Data
        // coreDataManager.toggleFavorite(suggestion: suggestions[index])
        
        // Haptic feedback
        let impactFeedback = UIImpactFeedbackGenerator(style: .light)
        impactFeedback.impactOccurred()
    }
    
    func copySuggestion(_ suggestion: GeneratedSuggestion) {
        UIPasteboard.general.string = suggestion.text
        
        // TODO: Track analytics event
        print("Copied suggestion: \(suggestion.text.prefix(50))...")
    }
    
    func clearSuggestions() {
        suggestions.removeAll()
    }
    
    func clearInput() {
        inputText = ""
    }
    
    // MARK: - Private Methods
    private func setupBindings() {
        // Clear error when user starts typing
        $inputText
            .dropFirst()
            .sink { [weak self] _ in
                self?.errorMessage = nil
                self?.showingError = false
            }
            .store(in: &cancellables)
    }
    
    private func performGeneration(mode: GenerationMode) async {
        isLoading = true
        errorMessage = nil
        showingError = false
        
        do {
            // TODO: Replace with actual API call
            let generatedSuggestions = try await generateMockSuggestions(
                context: inputText,
                style: selectedStyle,
                mode: mode
            )
            
            // Add new suggestions to the list
            suggestions.append(contentsOf: generatedSuggestions)
            
            // Clear input after successful generation
            inputText = ""
            
        } catch {
            errorMessage = error.localizedDescription
            showingError = true
        }
        
        isLoading = false
    }
    
    private func generateMockSuggestions(
        context: String,
        style: ChatStyle,
        mode: GenerationMode
    ) async throws -> [GeneratedSuggestion] {
        
        // Simulate network delay
        try await Task.sleep(nanoseconds: 2_000_000_000) // 2 seconds
        
        // Mock suggestions based on mode
        let mockTexts: [String]
        
        switch mode {
        case .pickup:
            mockTexts = [
                "I see you love adventures - what's the most spontaneous trip you've ever taken?",
                "A fellow photography enthusiast! What's your favorite subject to capture?",
                "Your hiking photos are incredible! What's your dream destination?"
            ]
        case .reply:
            mockTexts = [
                "That sounds amazing! I'd love to hear more about it.",
                "Wow, that's really interesting! Tell me more details."
            ]
        }
        
        return mockTexts.map { text in
            GeneratedSuggestion(text: text, style: style)
        }
    }
}

enum GenerationMode {
    case pickup
    case reply
}

// MARK: - Error Types
enum ChatError: LocalizedError {
    case networkError
    case invalidResponse
    case quotaExceeded
    case contentFiltered
    
    var errorDescription: String? {
        switch self {
        case .networkError:
            return "Unable to connect to the server. Please check your internet connection."
        case .invalidResponse:
            return "Received an invalid response from the server."
        case .quotaExceeded:
            return "You've reached your daily limit. Upgrade to premium for unlimited generations."
        case .contentFiltered:
            return "Content was filtered for safety. Please try with different text."
        }
    }
}