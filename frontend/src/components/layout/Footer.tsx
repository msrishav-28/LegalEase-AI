import Link from 'next/link';
import { FileText } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <FileText className="h-8 w-8 text-primary-600" />
              <span className="text-xl font-bold text-gray-900">LegalEase AI</span>
            </div>
            <p className="text-gray-600 mb-4 max-w-md">
              Advanced legal document analysis platform with multi-jurisdiction support 
              for Indian and US legal systems. Powered by AI for comprehensive legal insights.
            </p>
            <div className="text-sm text-gray-500">
              © 2024 LegalEase AI. All rights reserved.
            </div>
          </div>

          {/* Product */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">
              Product
            </h3>
            <ul className="space-y-2">
              <li>
                <Link href="/features" className="text-gray-600 hover:text-primary-600 transition-colors">
                  Features
                </Link>
              </li>
              <li>
                <Link href="/pricing" className="text-gray-600 hover:text-primary-600 transition-colors">
                  Pricing
                </Link>
              </li>
              <li>
                <Link href="/api" className="text-gray-600 hover:text-primary-600 transition-colors">
                  API
                </Link>
              </li>
              <li>
                <Link href="/integrations" className="text-gray-600 hover:text-primary-600 transition-colors">
                  Integrations
                </Link>
              </li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">
              Support
            </h3>
            <ul className="space-y-2">
              <li>
                <Link href="/help" className="text-gray-600 hover:text-primary-600 transition-colors">
                  Help Center
                </Link>
              </li>
              <li>
                <Link href="/docs" className="text-gray-600 hover:text-primary-600 transition-colors">
                  Documentation
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-gray-600 hover:text-primary-600 transition-colors">
                  Contact Us
                </Link>
              </li>
              <li>
                <Link href="/status" className="text-gray-600 hover:text-primary-600 transition-colors">
                  System Status
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-200">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex space-x-6 mb-4 md:mb-0">
              <Link href="/privacy" className="text-sm text-gray-600 hover:text-primary-600 transition-colors">
                Privacy Policy
              </Link>
              <Link href="/terms" className="text-sm text-gray-600 hover:text-primary-600 transition-colors">
                Terms of Service
              </Link>
              <Link href="/security" className="text-sm text-gray-600 hover:text-primary-600 transition-colors">
                Security
              </Link>
            </div>
            <div className="text-sm text-gray-500">
              Built with ❤️ for legal professionals
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}