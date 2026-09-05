import React, { useState, useRef, useEffect } from 'react';
import {
  Bot,
  User,
  Send,
  Sparkles,
  Database,
  ShieldCheck,
  ChevronDown,
  ChevronRight,
  Download,
  Trash2,
  Copy,
  Check,
  Code
} from 'lucide-react';
import { queryAssistant } from '../services/api';
import { AssistantMessage } from '../types';
import RiskBadge from '../components/RiskBadge';

const PROMPT_PILLS = [
  'What happened on the dock today?',
  'Which bay needs attention right now?',
  'Show me any dropped or thrown boxes',
  'What should we coach the team on during shift huddle?',
  'Why was the Bay 2 event flagged as high risk?',
  'Give me a quick shift handoff summary',
  'Are safe handling numbers improving this week?',
  'Show proper stacking rules for heavy pallets',
];

export default function AIAssistant() {
  const [messages, setMessages] = useState<AssistantMessage[]>([
    {
      id: 'msg-init',
      role: 'assistant',
      content:
        "Hey there! I'm your Shift Assistant for the warehouse floor. I monitor our dock camera logs, flagged handling incidents, and bay activity in real time. Ask me about today's high-risk flags, how specific bays are doing, or coaching points for the crew.",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      sources: ['Dock Camera Logs', 'Shift Incidents'],
      tools_called: ['get_statistics()'],
      confidence: 'high',
    },
  ]);
  const [input, setInput] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [expandedToolId, setExpandedToolId] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (queryText?: string) => {
    const textToSend = (queryText || input).trim();
    if (!textToSend || loading) return;

    const userMessage: AssistantMessage = {
      id: `usr-${Date.now()}`,
      role: 'user',
      content: textToSend,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await queryAssistant(textToSend);
      setMessages((prev) => [...prev, response]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: 'assistant',
          content: 'I encountered an error accessing the event database. Please try again.',
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleClearChat = () => {
    setMessages([
      {
        id: 'msg-init-cleared',
        role: 'assistant',
        content: 'Chat session reset. How can I assist you with warehouse safety telemetry?',
        timestamp: new Date().toLocaleTimeString(),
        sources: ['event_database'],
      },
    ]);
  };

  const handleExportTranscript = () => {
    const transcript = messages
      .map(
        (m) =>
          `[${m.timestamp || ''}] ${m.role.toUpperCase()}:\n${m.content || m.response}\n`
      )
      .join('\n---\n\n');

    const blob = new Blob([transcript], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ai_supervisor_transcript_${Date.now()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Helper to render basic markdown formatting cleanly
  const renderMarkdown = (text: string) => {
    const lines = text.split('\n');
    return lines.map((line, idx) => {
      if (line.startsWith('### ')) {
        return (
          <h4 key={idx} className="font-bold text-slate-900 text-sm mt-2 mb-1">
            {line.replace('### ', '')}
          </h4>
        );
      }
      if (line.startsWith('## ') || line.startsWith('# ')) {
        return (
          <h3 key={idx} className="font-bold text-slate-900 text-base mt-2 mb-1">
            {line.replace(/^#+ /, '')}
          </h3>
        );
      }
      if (line.startsWith('- ') || line.startsWith('* ')) {
        const itemContent = line.slice(2);
        return (
          <li key={idx} className="ml-4 list-disc text-slate-700 text-xs leading-relaxed my-0.5">
            <span dangerouslySetInnerHTML={{ __html: formatBold(itemContent) }} />
          </li>
        );
      }
      if (/^\d+\.\s/.test(line)) {
        return (
          <p key={idx} className="text-slate-700 text-xs leading-relaxed my-1">
            <span dangerouslySetInnerHTML={{ __html: formatBold(line) }} />
          </p>
        );
      }
      if (!line.trim()) {
        return <div key={idx} className="h-1.5" />;
      }
      return (
        <p key={idx} className="text-slate-700 text-xs leading-relaxed my-0.5">
          <span dangerouslySetInnerHTML={{ __html: formatBold(line) }} />
        </p>
      );
    });
  };

  const formatBold = (str: string) => {
    return str
      .replace(/\*\*(.*?)\*\*/g, '<strong class="text-slate-900 font-bold">$1</strong>')
      .replace(/`([^`]+)`/g, '<code class="px-1.5 py-0.5 rounded bg-slate-100 text-blue-700 font-mono text-[11px]">$1</code>');
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-w-5xl mx-auto bg-white rounded-3xl border border-slate-200/90 shadow-xs overflow-hidden">
      {/* Assistant Header */}
      <div className="p-4 px-6 border-b border-slate-800 bg-slate-900 text-white flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-white">Shift Supervisor Assistant</h2>
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-400/30">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Live Dock Logs Connected
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              Direct access to camera logs, safety incidents, and bay activity across Bays 1–6
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleExportTranscript}
            className="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800 transition-colors"
            title="Export Conversation Transcript"
          >
            <Download className="w-4 h-4" />
          </button>
          <button
            onClick={handleClearChat}
            className="p-2 text-slate-400 hover:text-rose-400 rounded-xl hover:bg-slate-800 transition-colors"
            title="Clear Chat"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/60">
        {messages.map((msg) => {
          const isUser = msg.role === 'user';
          const content = msg.content || msg.response || '';

          return (
            <div
              key={msg.id}
              className={`flex gap-3.5 ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start group`}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 shadow-xs ${
                  isUser
                    ? 'bg-slate-900 text-white'
                    : 'bg-white text-blue-600 border border-slate-200'
                }`}
              >
                {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              {/* Message Bubble */}
              <div className={`max-w-[85%] space-y-2`}>
                <div
                  className={`p-4 rounded-2xl text-xs ${
                    isUser
                      ? 'bg-slate-900 text-white rounded-tr-xs shadow-sm'
                      : 'bg-white border border-slate-200/90 text-slate-800 rounded-tl-xs shadow-xs'
                  }`}
                >
                  {isUser ? (
                    <p className="text-xs leading-relaxed">{content}</p>
                  ) : (
                    <div>{renderMarkdown(content)}</div>
                  )}
                </div>

                {/* Grounded Tool Execution & Sources Bar (For Assistant) */}
                {!isUser && (
                  <div className="flex flex-wrap items-center gap-2 text-[10px] text-slate-500 pl-1">
                    {/* Tools Called Pill */}
                    {msg.tools_called && msg.tools_called.length > 0 && (
                      <button
                        onClick={() =>
                          setExpandedToolId(expandedToolId === msg.id ? null : msg.id)
                        }
                        className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-slate-100 border border-slate-200 hover:border-slate-300 text-blue-600 font-mono cursor-pointer transition-colors"
                      >
                        <Code className="w-3 h-3" />
                        <span>Tools: {msg.tools_called.join(', ')}</span>
                        {expandedToolId === msg.id ? (
                          <ChevronDown className="w-3 h-3" />
                        ) : (
                          <ChevronRight className="w-3 h-3" />
                        )}
                      </button>
                    )}

                    {/* Sources Badge */}
                    {msg.sources && msg.sources.length > 0 && (
                      <span className="flex items-center gap-1 text-slate-500">
                        <Database className="w-3 h-3 text-slate-400" />
                        Sources: {msg.sources.join(', ')}
                      </span>
                    )}

                    {/* Copy Button */}
                    <button
                      onClick={() => handleCopy(msg.id, content)}
                      className="text-slate-400 hover:text-slate-600 ml-auto flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      {copiedId === msg.id ? (
                        <>
                          <Check className="w-3 h-3 text-emerald-600" /> Copied
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" /> Copy
                        </>
                      )}
                    </button>
                  </div>
                )}

                {/* Collapsible Telemetry JSON Viewer */}
                {!isUser && expandedToolId === msg.id && msg.data_used && (
                  <div className="p-3 bg-slate-900 rounded-2xl border border-slate-800 text-[11px] font-mono text-emerald-400 space-y-1 overflow-x-auto">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block">
                      Camera Log & Event Data:
                    </span>
                    <pre className="text-slate-300 text-[10px]">
                      {JSON.stringify(msg.data_used, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* Loading Indicator */}
        {loading && (
          <div className="flex gap-3.5 items-start">
            <div className="w-8 h-8 rounded-xl bg-white text-blue-600 border border-slate-200 flex items-center justify-center shrink-0">
              <Bot className="w-4 h-4" />
            </div>
            <div className="p-4 rounded-2xl bg-white border border-slate-200 rounded-tl-xs shadow-xs flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" />
              <span
                className="w-2 h-2 rounded-full bg-blue-500 animate-bounce"
                style={{ animationDelay: '0.2s' }}
              />
              <span
                className="w-2 h-2 rounded-full bg-blue-500 animate-bounce"
                style={{ animationDelay: '0.4s' }}
              />
              <span className="text-xs text-slate-500 ml-1">Checking dock logs...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompt Pills */}
      <div className="p-3 bg-white border-t border-slate-100 flex gap-2 overflow-x-auto shrink-0 scrollbar-none">
        <span className="text-[11px] font-bold text-slate-500 flex items-center gap-1 pl-2 shrink-0">
          <Sparkles className="w-3.5 h-3.5 text-blue-600" />
          Suggested:
        </span>
        {PROMPT_PILLS.map((pill, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(pill)}
            className="px-3.5 py-1 rounded-full bg-slate-50 hover:bg-slate-100 text-slate-700 hover:text-slate-900 border border-slate-200 text-xs whitespace-nowrap transition-colors shadow-2xs font-medium"
          >
            {pill}
          </button>
        ))}
      </div>

      {/* Input Box */}
      <div className="p-4 bg-white border-t border-slate-100 shrink-0">
        <div className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask AI supervisor about events, loading bay risks, or safety rules..."
            disabled={loading}
            className="w-full pl-5 pr-14 py-3 bg-slate-50 border border-slate-200 rounded-full text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:bg-white transition-all shadow-inner"
          />
          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || loading}
            className="absolute right-2 p-2 bg-slate-900 hover:bg-slate-800 text-white rounded-full disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-sm active:scale-95"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
