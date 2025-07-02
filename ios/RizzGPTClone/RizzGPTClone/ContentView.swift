import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "heart.fill")
                .font(.system(size: 60))
                .foregroundColor(.pink)
            
            Text("RizzGPT Clone")
                .font(.largeTitle)
                .fontWeight(.bold)
                .foregroundColor(.white)
            
            Text("AI-Powered Dating Assistant")
                .font(.headline)
                .foregroundColor(.gray)
            
            Text("v1.0")
                .font(.caption)
                .foregroundColor(.gray)
                .padding(.top, 40)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.black)
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
            .preferredColorScheme(.dark)
    }
}