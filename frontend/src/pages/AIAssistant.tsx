import { useState, useRef, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import type { ApiResponse, Conversation, AIMessage } from '../types';
import { Plus, Trash2, Send } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export default function AIAssistant() {
  const queryClient = useQueryClient();
  const [activeConv, setActiveConv] = useState<number | null>(null);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [showMarket, setShowMarket] = useState(true);
  const [showPortfolio, setShowPortfolio] = useState(true);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Conversations
  const { data: convData } = useQuery({
    queryKey: ['ai', 'conversations'],
    queryFn: () => api.get<ApiResponse<Conversation[]>>('/ai/conversations'),
  });
  const conversations = convData?.data ?? [];

  // Messages for active conversation
  const { data: msgData, refetch: refetchMsgs } = useQuery({
    queryKey: ['ai', 'messages', activeConv],
    queryFn: () => api.get<ApiResponse<AIMessage[]>>(`/ai/conversations/${activeConv}/messages`),
    enabled: !!activeConv,
  });
  const messages = msgData?.data ?? [];

  // Create conversation
  const createConv = useMutation({
    mutationFn: () => api.post<ApiResponse<Conversation>>('/ai/conversations'),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ['ai', 'conversations'] });
      setActiveConv(res.data?.id ?? null);
    },
  });

  // Delete conversation
  const deleteConv = useMutation({
    mutationFn: (id: number) => api.delete(`/ai/conversations/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai', 'conversations'] });
      if (activeConv === null) queryClient.invalidateQueries({ queryKey: ['ai', 'messages', activeConv] });
      setActiveConv(null);
    },
  });

  // Send message
  const sendMessage = async () => {
    if (!input.trim()) return;
    const message = input;
    setInput('');
    setIsStreaming(true);
    setStreaming('');

    try {
      let convId = activeConv;
      if (!convId) {
        const res = await api.post<ApiResponse<Conversation>>('/ai/conversations');
        convId = res.data?.id;
        setActiveConv(convId ?? null);
        queryClient.invalidateQueries({ queryKey: ['ai', 'conversations'] });
      }

      const response = await fetch('/api/v1/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_id: convId,
          message,
          context_hints: {
            include_market: showMarket,
            include_portfolio: showPortfolio,
          },
        }),
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let full = '';
      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;
        full += decoder.decode(value, { stream: true });
        setStreaming(full);
      }
    } catch (e) {
      setStreaming('*AI 服务暂时不可用，请稍后重试*');
    } finally {
      setIsStreaming(false);
      refetchMsgs();
    }
  };

  // Auto scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streaming]);

  return (
    <div className="flex h-[calc(100vh-80px)] gap-4">
      {/* Sidebar */}
      <div className="w-56 flex-shrink-0 flex flex-col rounded-xl overflow-hidden" style={{ backgroundColor: 'var(--bg-card)' }}>
        <div className="p-3 border-b" style={{ borderColor: 'var(--border-color)' }}>
          <button
            onClick={() => createConv.mutate()}
            className="w-full flex items-center justify-center gap-1 px-3 py-2 rounded-lg text-sm font-medium hover:opacity-80"
            style={{ backgroundColor: 'var(--accent-green)', color: '#000' }}
          >
            <Plus size={14} /> 新建对话
          </button>
        </div>
        <div className="flex-1 overflow-y-auto">
          {conversations.map((conv) => (
            <div
              key={conv.id}
              onClick={() => setActiveConv(conv.id)}
              className="flex items-center justify-between px-3 py-2.5 cursor-pointer hover:opacity-80 text-sm"
              style={{
                backgroundColor: conv.id === activeConv ? 'var(--bg-hover)' : 'transparent',
                color: conv.id === activeConv ? 'var(--text-primary)' : 'var(--text-secondary)',
              }}
            >
              <span className="truncate">{conv.title || 'New Conversation'}</span>
              <button
                onClick={(e) => { e.stopPropagation(); deleteConv.mutate(conv.id); }}
                className="p-1 rounded opacity-0 hover:opacity-100"
              >
                <Trash2 size={12} style={{ color: 'var(--accent-red)' }} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col rounded-xl overflow-hidden" style={{ backgroundColor: 'var(--bg-card)' }}>
        {/* Context Toggles */}
        <div className="flex gap-3 px-4 py-2 border-b" style={{ borderColor: 'var(--border-color)' }}>
          <label className="flex items-center gap-1.5 text-xs cursor-pointer" style={{ color: 'var(--text-secondary)' }}>
            <input type="checkbox" checked={showMarket} onChange={(e) => setShowMarket(e.target.checked)} />
            市场数据
          </label>
          <label className="flex items-center gap-1.5 text-xs cursor-pointer" style={{ color: 'var(--text-secondary)' }}>
            <input type="checkbox" checked={showPortfolio} onChange={(e) => setShowPortfolio(e.target.checked)} />
            持仓数据
          </label>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className="max-w-[80%] rounded-xl px-4 py-3 text-sm"
                style={{
                  backgroundColor: msg.role === 'user' ? 'var(--accent-green)' : 'var(--bg-hover)',
                  color: msg.role === 'user' ? '#000' : 'var(--text-primary)',
                }}
              >
                {msg.role === 'assistant' ? (
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                ) : (
                  <p>{msg.content}</p>
                )}
              </div>
            </div>
          ))}
          {isStreaming && streaming && (
            <div className="flex justify-start">
              <div className="max-w-[80%] rounded-xl px-4 py-3 text-sm" style={{ backgroundColor: 'var(--bg-hover)', color: 'var(--text-primary)' }}>
                <ReactMarkdown>{streaming}</ReactMarkdown>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t" style={{ borderColor: 'var(--border-color)' }}>
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              placeholder="输入问题，如：分析我的持仓风险..."
              disabled={isStreaming}
              className="flex-1 px-4 py-2.5 rounded-xl text-sm outline-none border"
              style={{ backgroundColor: 'var(--bg-primary)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }}
            />
            <button
              onClick={sendMessage}
              disabled={isStreaming || !input.trim()}
              className="px-4 py-2.5 rounded-xl disabled:opacity-30"
              style={{ backgroundColor: 'var(--accent-green)', color: '#000' }}
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
