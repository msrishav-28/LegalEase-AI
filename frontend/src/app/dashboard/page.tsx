import MainLayout from '@/components/layout/MainLayout';
import { BarChart3, FileText, Clock, TrendingUp } from 'lucide-react';

export default function DashboardPage() {
  // Mock data - in real app this would come from API
  const stats = [
    {
      name: 'Total Documents',
      value: '24',
      change: '+12%',
      changeType: 'positive' as const,
      icon: FileText,
    },
    {
      name: 'Analyses Completed',
      value: '18',
      change: '+8%',
      changeType: 'positive' as const,
      icon: BarChart3,
    },
    {
      name: 'Avg. Processing Time',
      value: '2.4m',
      change: '-15%',
      changeType: 'positive' as const,
      icon: Clock,
    },
    {
      name: 'Risk Score Trend',
      value: '7.2/10',
      change: '-5%',
      changeType: 'positive' as const,
      icon: TrendingUp,
    },
  ];

  const recentDocuments = [
    {
      id: '1',
      name: 'Service Agreement - TechCorp',
      type: 'contract',
      jurisdiction: 'india',
      status: 'completed',
      uploadedAt: '2024-01-15T10:30:00Z',
    },
    {
      id: '2',
      name: 'NDA - StartupXYZ',
      type: 'nda',
      jurisdiction: 'usa',
      status: 'processing',
      uploadedAt: '2024-01-15T09:15:00Z',
    },
    {
      id: '3',
      name: 'Partnership MOU',
      type: 'mou',
      jurisdiction: 'cross_border',
      status: 'completed',
      uploadedAt: '2024-01-14T16:45:00Z',
    },
  ];

  return (
    <MainLayout>
      <div className="p-6">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Overview of your legal document analysis</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat) => (
            <div key={stat.name} className="card">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <stat.icon className="h-6 w-6 text-primary-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                  <div className="flex items-baseline">
                    <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
                    <p className={`ml-2 text-sm font-medium ${
                      stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {stat.change}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Recent Documents */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">Recent Documents</h2>
            <a href="/documents" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
              View all
            </a>
          </div>
          
          <div className="overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Document
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Jurisdiction
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Uploaded
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {recentDocuments.map((doc) => (
                  <tr key={doc.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{doc.name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        {doc.type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        doc.jurisdiction === 'india' ? 'bg-orange-100 text-orange-800' :
                        doc.jurisdiction === 'usa' ? 'bg-blue-100 text-blue-800' :
                        'bg-purple-100 text-purple-800'
                      }`}>
                        {doc.jurisdiction}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        doc.status === 'completed' ? 'bg-green-100 text-green-800' :
                        doc.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {doc.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(doc.uploadedAt).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}