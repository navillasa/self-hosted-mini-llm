import { useState, useEffect, useRef } from 'react';
import { llm, auth } from '../api';

export default function Chat({ user, onLogout }) {
  const [messages, setMessages] = useState([]);
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [usage, setUsage] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchUsage();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchUsage = async () => {
    try {
      const response = await auth.getCurrentUser();
      setUsage(response.data.usage);
    } catch (error) {
      console.error('Failed to fetch usage:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim() || loading) return;

    const userMessage = { role: 'user', content: prompt };
    setMessages((prev) => [...prev, userMessage]);
    setPrompt('');
    setLoading(true);

    try {
      const response = await llm.generate(prompt);
      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        inferenceTime: response.data.inference_time_seconds,
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setUsage(response.data.usage);
    } catch (error) {
      const errorMessage = {
        role: 'error',
        content: error.response?.data?.detail || 'Failed to generate response',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-4 py-3">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <h1 className="text-xl font-bold text-white">Mini LLM</h1>
            {user.user && (
              <div className="flex items-center space-x-2">
                {user.user.avatar_url && (
                  <img
                    src={user.user.avatar_url}
                    alt={user.user.username}
                    className="w-8 h-8 rounded-full"
                  />
                )}
                <span className="text-gray-300 text-sm">{user.user.username}</span>
              </div>
            )}
          </div>

          <button
            onClick={onLogout}
            className="text-gray-400 hover:text-white text-sm transition"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Usage Stats */}
      {usage && (
        <div className="bg-gray-800 border-b border-gray-700 px-4 py-2">
          <div className="max-w-4xl mx-auto flex items-center justify-between text-sm">
            <div className="text-gray-400">
              Today: <span className="text-white font-semibold">{usage.requests_today}</span>
              <span className="text-gray-500"> / {usage.limit_per_day}</span>
            </div>
            <div className="text-gray-400">
              Last minute: <span className="text-white font-semibold">{usage.requests_last_minute}</span>
              <span className="text-gray-500"> / {usage.limit_per_minute}</span>
            </div>
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 ? (
            <div className="text-center text-gray-500 mt-12">
              <p className="text-lg mb-2">Start a conversation</p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-3xl rounded-lg px-4 py-3 ${
                    message.role === 'user'
                      ? 'bg-purple-600 text-white'
                      : message.role === 'error'
                      ? 'bg-red-900 text-red-200'
                      : 'bg-gray-800 text-gray-100'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  {message.inferenceTime && (
                    <div className="text-xs text-gray-400 mt-2">
                      Generated in {message.inferenceTime}s
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-800 text-gray-100 rounded-lg px-4 py-3">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-100"></div>
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200"></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="bg-gray-800 border-t border-gray-700 px-4 py-4">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <div className="flex space-x-2">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Ask anything..."
              disabled={loading}
              className="flex-1 bg-gray-900 text-white rounded-lg px-4 py-3 border border-gray-700 focus:outline-none focus:border-purple-500 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={loading || !prompt.trim()}
              className="bg-purple-600 hover:bg-purple-700 text-white font-semibold px-6 py-3 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
