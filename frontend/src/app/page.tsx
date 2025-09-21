import Link from 'next/link';
import { FileText, BarChart3, Search, Users, ArrowRight, CheckCircle } from 'lucide-react';

export default function Home() {
  const features = [
    {
      icon: FileText,
      title: 'Document Analysis',
      description: 'AI-powered analysis of legal documents with jurisdiction-specific insights',
    },
    {
      icon: BarChart3,
      title: 'Risk Assessment',
      description: 'Comprehensive risk scoring and identification for better decision making',
    },
    {
      icon: Search,
      title: 'Semantic Search',
      description: 'Find similar clauses and legal concepts across your document library',
    },
    {
      icon: Users,
      title: 'Real-time Collaboration',
      description: 'Work together with your team on document analysis and review',
    },
  ];

  const jurisdictions = [
    {
      name: 'India',
      description: 'Indian Contract Act, GST compliance, stamp duty calculations',
      color: 'bg-orange-100 text-orange-800',
    },
    {
      name: 'United States',
      description: 'UCC compliance, federal regulations, state law analysis',
      color: 'bg-blue-100 text-blue-800',
    },
    {
      name: 'Cross-border',
      description: 'Comparative analysis for international transactions',
      color: 'bg-purple-100 text-purple-800',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <FileText className="h-8 w-8 text-primary-600" />
              <span className="text-xl font-bold text-gray-900">LegalEase AI</span>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/login" className="text-gray-700 hover:text-primary-600 transition-colors">
                Sign In
              </Link>
              <Link href="/register" className="btn-primary">
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 bg-gradient-to-br from-primary-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              AI-Powered Legal
              <span className="text-primary-600 block">Document Analysis</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Analyze legal documents with jurisdiction-specific insights for Indian and US legal systems. 
              Get comprehensive risk assessments, obligation extraction, and real-time collaboration.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/register" className="btn-primary text-lg px-8 py-3">
                Start Free Trial
                <ArrowRight className="ml-2 w-5 h-5" />
              </Link>
              <Link href="/demo" className="btn-secondary text-lg px-8 py-3">
                Watch Demo
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Powerful Features for Legal Professionals
            </h2>
            <p className="text-xl text-gray-600">
              Everything you need to analyze and manage legal documents efficiently
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="card text-center">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <feature.icon className="w-6 h-6 text-primary-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Jurisdiction Support */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Multi-Jurisdiction Support
            </h2>
            <p className="text-xl text-gray-600">
              Specialized analysis for different legal systems
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {jurisdictions.map((jurisdiction, index) => (
              <div key={index} className="card">
                <div className="flex items-center mb-4">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${jurisdiction.color}`}>
                    {jurisdiction.name}
                  </span>
                </div>
                <p className="text-gray-600">{jurisdiction.description}</p>
                <div className="mt-4 flex items-center text-primary-600">
                  <CheckCircle className="w-4 h-4 mr-2" />
                  <span className="text-sm font-medium">Fully Supported</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Transform Your Legal Workflow?
          </h2>
          <p className="text-xl text-primary-100 mb-8">
            Join legal professionals who trust LegalEase AI for document analysis
          </p>
          <Link href="/register" className="bg-white text-primary-600 hover:bg-gray-100 font-medium py-3 px-8 rounded-lg transition-colors inline-flex items-center">
            Get Started Today
            <ArrowRight className="ml-2 w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <FileText className="h-6 w-6" />
              <span className="text-lg font-bold">LegalEase AI</span>
            </div>
            <div className="text-gray-400 text-sm">
              © 2024 LegalEase AI. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}