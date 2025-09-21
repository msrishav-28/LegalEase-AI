import React from 'react';
import { clsx } from 'clsx';
import { JurisdictionBadge as JurisdictionBadgeType } from '@/types';

interface JurisdictionBadgeProps {
  badge: JurisdictionBadgeType;
  size?: 'sm' | 'md' | 'lg';
  showConfidence?: boolean;
  className?: string;
}

const colorClasses = {
  blue: 'bg-blue-100 text-blue-800 border-blue-200',
  green: 'bg-green-100 text-green-800 border-green-200',
  orange: 'bg-orange-100 text-orange-800 border-orange-200',
  purple: 'bg-purple-100 text-purple-800 border-purple-200',
};

const sizeClasses = {
  sm: 'px-2 py-1 text-xs',
  md: 'px-2.5 py-1.5 text-sm',
  lg: 'px-3 py-2 text-base',
};

export default function JurisdictionBadge({
  badge,
  size = 'sm',
  showConfidence = true,
  className
}: JurisdictionBadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full border font-medium',
        colorClasses[badge.color],
        sizeClasses[size],
        className
      )}
      title={`Jurisdiction: ${badge.label} (${Math.round(badge.confidence * 100)}% confidence)`}
    >
      <span>{badge.label}</span>
      {showConfidence && (
        <span className="ml-1 opacity-75">
          {Math.round(badge.confidence * 100)}%
        </span>
      )}
    </span>
  );
}