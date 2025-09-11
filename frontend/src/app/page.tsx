export default function Home() {
  return (
    <main className="container mx-auto px-4 py-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to LegalEase AI
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Legal document analysis platform with multi-jurisdiction support
        </p>
        <div className="card max-w-md mx-auto">
          <h2 className="text-2xl font-semibold mb-4">Getting Started</h2>
          <p className="text-gray-600 mb-4">
            Upload your legal documents and get AI-powered analysis with 
            jurisdiction-specific insights for Indian and US legal systems.
          </p>
          <button className="btn-primary w-full">
            Upload Document
          </button>
        </div>
      </div>
    </main>
  );
}