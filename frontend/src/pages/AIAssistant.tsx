import { useState, useRef, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import type { ApiResponse, Conversation, AIMessage } from '../types';
import { Plus, Trash2, Send, Bot } from 'lucide-react';
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

      const API_BASE = import.meta.env.VITE_API_BASE || '/api/v1';
      const response = await fetch(`${API_BASE}/ai/chat`, {
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
      <div className="w-56 flex-shrink-0 flex flex-col rounded-xl overflow-hidden bg-card">
        <div className="p-3 border-b border-border">
          <button
            onClick={() => createConv.mutate()}
            className="w-full flex items-center justify-center gap-1 px-3 py-2 rounded-lg text-sm font-medium bg-brand text-black hover:opacity-90 transition-all duration-200"
          >
            <Plus size={14} /> 新建对话
          </button>
        </div>
        <div className="flex-1 overflow-y-auto">
          {conversations.length === 0 ? (
            <div className="px-3 py-8 text-center">
              <p className="text-xs text-muted-text">暂无对话</p>
            </div>
          ) : (
            conversations.map((conv) => (
              <div
                key={conv.id}
                onClick={() => setActiveConv(conv.id)}
                className={`flex items-center justify-between px-3 py-2.5 cursor-pointer text-sm transition-all duration-200 ${
                  conv.id === activeConv
                    ? 'bg-hover text-text'
                    : 'text-secondary-text hover:bg-hover hover:text-text'
                }`}
              >
                <span className="truncate">{conv.title || 'New Conversation'}</span>
                <button
                  onClick={(e) => { e.stopPropagation(); deleteConv.mutate(conv.id); }}
                  className="p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-danger/20 transition-all duration-200"
                  aria-label="删除对话"
                >
                  <Trash2 size={12} className="text-danger" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col rounded-xl overflow-hidden bg-card">
        {/* Context Toggles */}
        <div className="flex gap-3 px-4 py-2 border-b border-border">
          <label className="flex items-center gap-1.5 text-xs cursor-pointer text-secondary-text hover:text-text transition-colors">
            <input type="checkbox" checked={showMarket} onChange={(e) => setShowMarket(e.target.checked)} />
            市场数据
          </label>
          <label className="flex items-center gap-1.5 text-xs cursor-pointer text-secondary-text hover:text-text transition-colors">
            <input type="checkbox" checked={showPortfolio} onChange={(e) => setShowPortfolio(e.target.checked)} />
            持仓数据
          </label>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {!activeConv ? (
            /* Welcome / empty state */
            <div className="flex flex-col items-center justify-center h-full text-center">
              <Bot size={48} className="text-muted-text mb-4" />
              <h2 className="text-xl font-semibold mb-2">CSQAQ AI 助手</h2>
              <p className="text-sm text-secondary-text max-w-md">
                我可以帮你分析市场行情、评估持仓风险、解答饰品相关问题。
                点击左侧「新建对话」开始，或直接输入问题。
              </p>
              <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
                {[
                  '当前市场行情如何？',
                  '分析我的持仓风险',
                  '最近哪些饰品在涨？',
                  'AK-47 夜愿价格走势',
                ].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => { setInput(suggestion); }}
                    className="px-4 py-2 rounded-lg bg-hover text-secondary-text hover:bg-border hover:text-text transition-all duration-200"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          ) : messages.length === 0 && !isStreaming ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <Bot size={40} className="text-muted-text mb-3" />
              <p className="text-sm text-secondary-text">开始你的第一个问题</p>
            </div>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[80%] rounded-xl px-4 py-3 text-sm ${
                    msg.role === 'user'
                      ? 'bg-brand text-black'
                      : 'bg-hover text-text'
                  }`}
                >
                  {msg.role === 'assistant' ? (
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  ) : (
                    <p>{msg.content}</p>
                  )}
                </div>
              </div>
            ))
          )}
          {isStreaming && streaming && (
            <div className="flex justify-start">
              <div className="max-w-[80%] rounded-xl px-4 py-3 text-sm bg-hover text-text">
                <ReactMarkdown>{streaming}</ReactMarkdown>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-border">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              placeholder="输入问题，如：分析我的持仓风险..."
              disabled={isStreaming}
              className="flex-1 px-4 py-2.5 rounded-xl text-sm outline-none border border-border bg-primary text-text placeholder-muted-text focus:border-brand focus:ring-1 focus:ring-brand transition-all duration-200"
            />
            <button
              onClick={sendMessage}
              disabled={isStreaming || !input.trim()}
              className="px-4 py-2.5 rounded-xl disabled:opacity-30 bg-brand text-black hover:opacity-90 transition-all duration-200"
              aria-label="发送"
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
