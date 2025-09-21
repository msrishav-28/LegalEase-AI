'use client';

import React, { useState, useCallback, useRef } from 'react';
import { Upload, X, FileText, AlertCircle, CheckCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { DocumentType } from '@/types';
import { validateFiles, formatFileSize } from '@/lib/fileValidation';

interface UploadFile extends File {
  id: string;
  progress: number;
  status: 'pending' | 'uploading' | 'completed' | 'error';
  error?: string;
}

interface DocumentUploadProps {
  onUploadComplete?: (files: UploadFile[]) => void;
  onUploadProgress?: (fileId: string, progress: number) => void;
  onUploadError?: (fileId: string, error: string) => void;
  maxFileSize?: number; // in bytes
  allowedTypes?: string[];
  maxFiles?: number;
  className?: string;
}

const DEFAULT_MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
const DEFAULT_ALLOWED_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain',
];

export default function DocumentUpload({
  onUploadComplete,
  onUploadProgress,
  onUploadError,
  maxFileSize = DEFAULT_MAX_FILE_SIZE,
  allowedTypes = DEFAULT_ALLOWED_TYPES,
  maxFiles = 10,
  className,
}: DocumentUploadProps) {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const generateFileId = () => Math.random().toString(36).substr(2, 9);

  const processFiles = useCallback((fileList: FileList | File[]) => {
    const fileArray = Array.from(fileList);
    
    // Validate all files at once
    const validationResult = validateFiles(fileArray, {
      maxSize: maxFileSize,
      allowedTypes,
      maxFiles: maxFiles - files.length, // Account for already selected files
    });

    if (!validationResult.isValid) {
      // Show errors to user (you might want to use a toast notification here)
      console.error('Upload errors:', validationResult.errors);
      return;
    }

    const newFiles: UploadFile[] = [];
    const errors: string[] = [];

    fileArray.forEach((file) => {
      // Check for duplicates with existing files
      const isDuplicate = files.some(f => f.name === file.name && f.size === file.size);
      if (isDuplicate) {
        errors.push(`${file.name}: File already added`);
        return;
      }

      const uploadFile: UploadFile = Object.assign(file, {
        id: generateFileId(),
        progress: 0,
        status: 'pending' as const,
      });

      newFiles.push(uploadFile);
    });

    if (errors.length > 0) {
      console.error('Duplicate file errors:', errors);
    }

    if (newFiles.length > 0) {
      setFiles(prev => [...prev, ...newFiles]);
    }
  }, [files, maxFiles, maxFileSize, allowedTypes]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    const droppedFiles = e.dataTransfer.files;
    if (droppedFiles.length > 0) {
      processFiles(droppedFiles);
    }
  }, [processFiles]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files;
    if (selectedFiles && selectedFiles.length > 0) {
      processFiles(selectedFiles);
    }
    // Reset input value to allow selecting the same file again
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [processFiles]);

  const removeFile = useCallback((fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  }, []);

  const simulateUpload = async (file: UploadFile) => {
    // Simulate upload progress
    for (let progress = 0; progress <= 100; progress += 10) {
      await new Promise(resolve => setTimeout(resolve, 100));
      
      setFiles(prev => prev.map(f => 
        f.id === file.id 
          ? { ...f, progress, status: progress === 100 ? 'completed' : 'uploading' }
          : f
      ));
      
      onUploadProgress?.(file.id, progress);
    }
  };

  const startUpload = async () => {
    if (files.length === 0 || isUploading) return;

    setIsUploading(true);

    try {
      // Update all files to uploading status
      setFiles(prev => prev.map(f => ({ ...f, status: 'uploading' as const })));

      // Simulate uploading all files
      await Promise.all(files.map(file => simulateUpload(file)));

      onUploadComplete?.(files);
    } catch (error) {
      console.error('Upload failed:', error);
      setFiles(prev => prev.map(f => ({ 
        ...f, 
        status: 'error' as const,
        error: 'Upload failed. Please try again.'
      })));
    } finally {
      setIsUploading(false);
    }
  };

  const getStatusIcon = (status: UploadFile['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'uploading':
        return <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />;
      default:
        return <FileText className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: UploadFile['status']) => {
    switch (status) {
      case 'completed':
        return 'text-green-600';
      case 'error':
        return 'text-red-600';
      case 'uploading':
        return 'text-blue-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className={cn('space-y-4', className)}>
      {/* Drop Zone */}
      <div
        className={cn(
          'border-2 border-dashed rounded-lg p-8 text-center transition-colors',
          isDragOver
            ? 'border-primary-400 bg-primary-50'
            : 'border-gray-300 hover:border-gray-400'
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <div className="space-y-2">
          <p className="text-lg font-medium text-gray-900">
            Drop files here or{' '}
            <button
              type="button"
              className="text-primary-600 hover:text-primary-500 font-semibold"
              onClick={() => fileInputRef.current?.click()}
            >
              browse
            </button>
          </p>
          <p className="text-sm text-gray-500">
            Supports PDF, DOC, DOCX, TXT files up to {formatFileSize(maxFileSize)}
          </p>
          <p className="text-xs text-gray-400">
            Maximum {maxFiles} files allowed
          </p>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={allowedTypes.join(',')}
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-900">
              Selected Files ({files.length})
            </h3>
            {files.length > 0 && !isUploading && (
              <button
                onClick={startUpload}
                className="btn-primary text-sm"
                disabled={files.every(f => f.status === 'completed')}
              >
                Upload All
              </button>
            )}
          </div>

          <div className="space-y-2">
            {files.map((file) => (
              <div
                key={file.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center space-x-3 flex-1 min-w-0">
                  {getStatusIcon(file.status)}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {file.name}
                    </p>
                    <div className="flex items-center space-x-2 text-xs text-gray-500">
                      <span>{formatFileSize(file.size)}</span>
                      <span className={getStatusColor(file.status)}>
                        {file.status === 'uploading' ? `${file.progress}%` : file.status}
                      </span>
                    </div>
                    {file.error && (
                      <p className="text-xs text-red-600 mt-1">{file.error}</p>
                    )}
                  </div>
                </div>

                {/* Progress Bar */}
                {file.status === 'uploading' && (
                  <div className="w-24 mx-3">
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <div
                        className="bg-blue-500 h-1.5 rounded-full transition-all duration-300"
                        style={{ width: `${file.progress}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* Remove Button */}
                {file.status !== 'uploading' && (
                  <button
                    onClick={() => removeFile(file.id)}
                    className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                    aria-label={`Remove ${file.name}`}
                    title={`Remove ${file.name}`}
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}