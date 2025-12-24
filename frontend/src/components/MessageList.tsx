import React from 'react';
import { Message } from '@/types';
import { User, Bot, CheckCircle, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface Props {
  messages: Message[];
  streamingContent?: string;
}

export default function MessageList({ messages, streamingContent }: Props) {
  return (
    <div className="space-y-4">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex gap-3 ${
            message.role === 'user' ? 'justify-end' : 'justify-start'
          }`}
        >
          {message.role === 'assistant' && (
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
          )}

          <div
            className={`max-w-[70%] rounded-lg p-4 ${
              message.role === 'user'
                ? 'bg-blue-600 text-white'
                : 'bg-white border border-gray-200'
            }`}
          >
            <div className="prose prose-sm max-w-none">
              {message.role === 'assistant' ? (
                <ReactMarkdown>{message.content}</ReactMarkdown>
              ) : (
                <p className="m-0">{message.content}</p>
              )}
            </div>

            {message.classifier && (
              <div className="mt-3 pt-3 border-t border-gray-200 flex items-center gap-4 text-xs">
                <span className="flex items-center gap-1 text-gray-600">
                  <span className="font-semibold">Type:</span>
                  <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded">
                    {message.classifier}
                  </span>
                </span>
                {message.confidence_score && (
                  <span className="flex items-center gap-1 text-gray-600">
                    <CheckCircle className="w-3 h-3" />
                    <span className="font-semibold">Confidence:</span>
                    <span>{message.confidence_score}/10</span>
                  </span>
                )}
              </div>
            )}

            {message.reasoning && (
              <div className="mt-2 text-xs text-gray-500 italic">
                {message.reasoning}
              </div>
            )}
          </div>

          {message.role === 'user' && (
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center">
              <User className="w-5 h-5 text-gray-700" />
            </div>
          )}
        </div>
      ))}

      {streamingContent && (
        <div className="flex gap-3 justify-start">
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <Bot className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div className="max-w-[70%] rounded-lg p-4 bg-white border border-gray-200">
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown>{streamingContent}</ReactMarkdown>
            </div>
            <div className="mt-2 flex items-center gap-1 text-xs text-gray-500">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
              <span>Streaming...</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
