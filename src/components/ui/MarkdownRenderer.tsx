"use client";

import React, { useMemo, useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownRendererProps {
  content: string;
  className?: string;
  cacheKey?: string;
}

// Simple in-memory cache for markdown content
const markdownCache = new Map<string, JSX.Element>();

const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ 
  content, 
  className = '', 
  cacheKey 
}) => {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const renderedContent = useMemo(() => {
    if (!isMounted) return null;

    // Use cache if cacheKey is provided and content exists
    if (cacheKey && markdownCache.has(cacheKey)) {
      return markdownCache.get(cacheKey);
    }

    const components = {
      // Custom styling for code blocks
      code: ({ inline, className: classNameProp, children, ...props }: any) => {
        const match = /language-(\w+)/.exec(classNameProp || '');
        return !inline && match ? (
          <div className="my-4">
            <div className="bg-gray-800 text-gray-300 px-4 py-2 text-xs font-medium rounded-t-lg flex items-center justify-between">
              <span>{match[1]}</span>
              <span className="text-gray-500">Code</span>
            </div>
            <pre className="bg-gray-900 text-gray-100 p-4 rounded-b-lg overflow-x-auto">
              <code className={`language-${match[1]} text-sm`} {...props}>
                {children}
              </code>
            </pre>
          </div>
        ) : (
          <code className="bg-emerald-50 text-emerald-800 px-1.5 py-0.5 rounded text-sm font-mono border border-emerald-200" {...props}>
            {children}
          </code>
        );
      },
      // Custom styling for headings
      h1: ({ children }: any) => (
        <h1 className="text-3xl font-bold text-emerald-700 mb-4 mt-8 border-b border-emerald-200 pb-2">{children}</h1>
      ),
      h2: ({ children }: any) => (
        <h2 className="text-2xl font-semibold text-emerald-600 mb-3 mt-6">{children}</h2>
      ),
      h3: ({ children }: any) => (
        <h3 className="text-xl font-semibold text-gray-800 mb-2 mt-4 flex items-center">
          <span className="w-1 h-5 bg-emerald-500 rounded-full mr-2"></span>
          {children}
        </h3>
      ),
      h4: ({ children }: any) => (
        <h4 className="text-lg font-medium text-gray-700 mb-2 mt-3">{children}</h4>
      ),
      // Custom styling for lists
      ul: ({ children }: any) => (
        <ul className="list-disc list-inside space-y-1 mb-4 ml-4">{children}</ul>
      ),
      ol: ({ children }: any) => (
        <ol className="list-decimal list-inside space-y-1 mb-4 ml-4">{children}</ol>
      ),
      li: ({ children }: any) => (
        <li className="text-gray-700">{children}</li>
      ),
      // Custom styling for paragraphs
      p: ({ children }: any) => (
        <p className="text-gray-700 mb-3 leading-relaxed">{children}</p>
      ),
      // Custom styling for tables
      table: ({ children }: any) => (
        <div className="overflow-x-auto mb-6">
          <table className="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg shadow-sm">
            {children}
          </table>
        </div>
      ),
      thead: ({ children }: any) => (
        <thead className="bg-emerald-50">
          {children}
        </thead>
      ),
      th: ({ children }: any) => (
        <th className="px-4 py-3 text-left text-xs font-semibold text-emerald-700 uppercase tracking-wider">
          {children}
        </th>
      ),
      td: ({ children }: any) => (
        <td className="px-4 py-3 text-sm text-gray-700 border-b border-gray-100">
          {children}
        </td>
      ),
      // Custom styling for blockquotes
      blockquote: ({ children }: any) => (
        <blockquote className="border-l-4 border-blue-500 pl-4 italic text-gray-600 my-4">
          {children}
        </blockquote>
      ),
      // Custom styling for links
      a: ({ children, href }: any) => (
        <a 
          href={href} 
          className="text-blue-600 hover:text-blue-800 underline"
          target="_blank"
          rel="noopener noreferrer"
        >
          {children}
        </a>
      ),
      // Custom styling for strong/bold text
      strong: ({ children }: any) => (
        <strong className="font-semibold text-gray-900">{children}</strong>
      ),
      // Custom styling for emphasis/italic text
      em: ({ children }: any) => (
        <em className="italic text-gray-700">{children}</em>
      ),
    };

    const rendered = (
      <div className={`prose prose-lg max-w-none ${className}`}>
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={components}
        >
          {content}
        </ReactMarkdown>
      </div>
    );

    // Cache the rendered content if cacheKey is provided
    if (cacheKey) {
      markdownCache.set(cacheKey, rendered);
    }

    return rendered;
  }, [content, className, cacheKey, isMounted]);

  return (
    <div className="markdown-renderer">
      {renderedContent}
    </div>
  );
};

// Export cache management functions
export { markdownCache };
export default MarkdownRenderer;