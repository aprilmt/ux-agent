import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useSearchParams } from 'react-router-dom';
import axios from 'axios';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

const Chat: React.FC = () => {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState('triage');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const conversationId = searchParams.get('conversation');
    if (conversationId) {
      loadConversation(parseInt(conversationId));
    }
  }, [searchParams]);

  const loadConversation = async (conversationId: number) => {
    try {
      const response = await axios.get(`/api/ux-agent/conversations/${conversationId}`);
      setMessages(response.data.messages || []);
    } catch (error) {
      console.error('Failed to load conversation:', error);
    }
  };

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || loading) return;

    const userMessage: Message = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await axios.post('/api/ux-agent/chat', {
        message: inputMessage,
        agent_type: selectedAgent,
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        role: 'assistant',
        content: `Error: ${error.response?.data?.detail || 'Failed to send message'}`,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900">Please log in to access the chat</h1>
        </div>
      </div>
    );
  }

  if (!user.is_premium) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900">Premium subscription required</h1>
          <p className="mt-2 text-gray-600">Upgrade to premium to access the UX AI agents</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-lg">
        <div className="p-4">
          <h2 className="text-lg font-semibold text-gray-900">UX AI Agents</h2>
          <div className="mt-4 space-y-2">
            <button
              onClick={() => setSelectedAgent('triage')}
              className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium ${
                selectedAgent === 'triage'
                  ? 'bg-indigo-100 text-indigo-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              🎯 Triage Agent
            </button>
            <button
              onClick={() => setSelectedAgent('workflow')}
              className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium ${
                selectedAgent === 'workflow'
                  ? 'bg-indigo-100 text-indigo-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              🔄 Workflow Specialist
            </button>
            <button
              onClick={() => setSelectedAgent('thinking')}
              className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium ${
                selectedAgent === 'thinking'
                  ? 'bg-indigo-100 text-indigo-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              🧠 Strategic Thinker
            </button>
            <button
              onClick={() => setSelectedAgent('writing')}
              className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium ${
                selectedAgent === 'writing'
                  ? 'bg-indigo-100 text-indigo-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              ✍️ Writing Expert
            </button>
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white shadow-sm border-b px-6 py-4">
          <h1 className="text-xl font-semibold text-gray-900">
            Chat with UX AI Agent
          </h1>
          <p className="text-sm text-gray-500">
            Selected: {selectedAgent === 'triage' ? 'Triage Agent' : 
                      selectedAgent === 'workflow' ? 'Workflow Specialist' :
                      selectedAgent === 'thinking' ? 'Strategic Thinker' : 'Writing Expert'}
          </p>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 mt-8">
              <p>Start a conversation with the UX AI agent!</p>
              <p className="text-sm mt-2">Ask about UX workflows, strategic thinking, or content writing.</p>
            </div>
          )}
          
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-white text-gray-900 border border-gray-200'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                {message.timestamp && (
                  <p className={`text-xs mt-1 ${
                    message.role === 'user' ? 'text-indigo-200' : 'text-gray-500'
                  }`}>
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </p>
                )}
              </div>
            </div>
          ))}
          
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-900 border border-gray-200 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600"></div>
                  <p className="text-sm">AI is thinking...</p>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="bg-white border-t px-6 py-4">
          <form onSubmit={sendMessage} className="flex space-x-4">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask about UX workflows, strategy, or writing..."
              className="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !inputMessage.trim()}
              className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Chat;
