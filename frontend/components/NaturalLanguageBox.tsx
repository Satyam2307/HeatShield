"use client";

import React, { useState } from "react";
import { MessageSquare, Send, Sparkles, RefreshCw, AlertCircle } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";

export default function NaturalLanguageBox() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: (q: string) => apiClient.getExplanation(q),
    onSuccess: (data) => {
      setResult(data.explanation);
    },
  });

  const PRESETS = [
    "Why is this stop ranked first?",
    "Which five stops should receive shade?",
    "What are the most persistent heat locations?",
    "What changes if vulnerability receives more weight?",
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (question.trim() === "") return;
    mutation.mutate(question);
  };

  const handlePresetClick = (preset: string) => {
    setQuestion(preset);
    mutation.mutate(preset);
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="bg-red-100 text-red-700 p-1.5 rounded-lg">
            <MessageSquare className="h-4.5 w-4.5" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider block">
              ShadeStop Planning Assistant
            </h3>
            <p className="text-[10px] text-slate-400">
              Query rankings, persistence analytics, and weight logic using natural language.
            </p>
          </div>
        </div>
        <Sparkles className="h-4 w-4 text-amber-500 animate-pulse hidden sm:block" />
      </div>

      <div className="p-4 space-y-4">
        {/* Presets Grid */}
        <div className="space-y-1.5">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
            Suggested Queries
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {PRESETS.map((preset) => (
              <button
                key={preset}
                type="button"
                onClick={() => handlePresetClick(preset)}
                className="text-left text-xs bg-slate-50 hover:bg-slate-100 border border-slate-200 hover:border-slate-350 px-3 py-2 rounded-lg text-slate-700 font-medium transition-all truncate"
                title={preset}
              >
                {preset}
              </button>
            ))}
          </div>
        </div>

        {/* Form Input */}
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            placeholder="Ask a question (e.g., 'What are the top 5 stops?')..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={mutation.isPending}
            className="flex-1 px-3 py-2 border border-slate-250 rounded-lg text-xs focus:outline-none focus:border-red-500 bg-white disabled:bg-slate-50"
          />
          <button
            type="submit"
            disabled={mutation.isPending || question.trim() === ""}
            className="bg-slate-900 hover:bg-slate-800 disabled:bg-slate-200 text-white disabled:text-slate-400 px-3.5 py-2 rounded-lg transition-colors flex items-center justify-center shrink-0"
          >
            {mutation.isPending ? (
              <RefreshCw className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </button>
        </form>

        {/* Answer Output Bubble */}
        {(result || mutation.isPending || mutation.isError) && (
          <div className="border-t border-slate-100 pt-4">
            {mutation.isPending && (
              <div className="bg-slate-50 border border-slate-150 p-4 rounded-xl flex items-center justify-center gap-2.5 text-xs text-slate-500">
                <RefreshCw className="h-4 w-4 animate-spin text-red-500" />
                <span>Generating explanation from planning repository...</span>
              </div>
            )}

            {mutation.isError && (
              <div className="bg-red-50 border border-red-150 p-3.5 rounded-xl text-xs text-red-800 flex gap-2 items-start">
                <AlertCircle className="h-4 w-4 text-red-600 shrink-0 mt-0.5" />
                <span>Failed to generate explanation. Please try clicking a preset option.</span>
              </div>
            )}

            {result && !mutation.isPending && (
              <div className="bg-slate-900 border border-slate-850 p-4 rounded-xl text-xs text-slate-100 space-y-2 leading-relaxed">
                <div className="flex items-center gap-1 text-[9px] font-bold text-red-400 uppercase tracking-widest">
                  <Sparkles className="h-3 w-3" />
                  <span>Technical Explanation</span>
                </div>
                <p className="whitespace-pre-line text-slate-200">{result}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
