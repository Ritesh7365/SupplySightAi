"use client";

import { useState, type FormEvent } from "react";
import { useMutation } from "@tanstack/react-query";
import { MessageCircle, Sparkles, X } from "lucide-react";

import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

const SUGGESTIONS = [
  "Why did profit drop?",
  "Why is shipping delayed?",
  "Predict next month sales.",
  "Which products should be restocked?",
  "Which warehouses are inefficient?",
  "Show anomalies.",
];

type ChatMessage = { role: "user" | "assistant"; content: string; sources?: string[] };

export function AiInsightsPanel({ floating = false }: { floating?: boolean }) {
  const [open, setOpen] = useState(!floating);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "I am the SupplySight analytics copilot. Ask about revenue, shipping delays, restocking, forecasts, or anomalies.",
    },
  ]);

  const mutation = useMutation({
    mutationFn: (question: string) => api.askAi(question),
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.answer, sources: data.sources },
      ]);
    },
    onError: (err) => {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: err instanceof Error ? err.message : "Unable to answer right now.",
        },
      ]);
    },
  });

  function submit(question: string) {
    const q = question.trim();
    if (!q || mutation.isPending) return;
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setInput("");
    mutation.mutate(q);
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    submit(input);
  }

  const panel = (
    <Card className={cn("flex h-full flex-col", floating && "shadow-2xl")}>
      <CardHeader className="flex flex-row items-start justify-between gap-3 border-b border-border">
        <div>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Sparkles className="size-4 text-primary" />
            AI Copilot
          </CardTitle>
          <CardDescription>Natural language insights over analytics views</CardDescription>
        </div>
        {floating ? (
          <Button variant="ghost" size="sm" onClick={() => setOpen(false)} aria-label="Close">
            <X className="size-4" />
          </Button>
        ) : null}
      </CardHeader>
      <CardContent className="flex min-h-0 flex-1 flex-col gap-3 p-4">
        <div className="flex flex-wrap gap-2">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => submit(s)}
              className="rounded-full border border-border bg-muted/40 px-3 py-1 text-xs text-muted-foreground transition hover:bg-muted hover:text-foreground"
            >
              {s}
            </button>
          ))}
        </div>

        <div className="min-h-[16rem] flex-1 space-y-3 overflow-y-auto rounded-xl border border-border bg-muted/20 p-3">
          {messages.map((m, i) => (
            <div
              key={`${m.role}-${i}`}
              className={cn(
                "max-w-[90%] rounded-2xl px-3 py-2 text-sm",
                m.role === "user"
                  ? "ml-auto bg-primary text-primary-foreground"
                  : "bg-background text-foreground shadow-sm",
              )}
            >
              <p className="whitespace-pre-wrap">{m.content}</p>
              {m.sources?.length ? (
                <p className="mt-2 text-[11px] text-muted-foreground">
                  Sources: {m.sources.join(" · ")}
                </p>
              ) : null}
            </div>
          ))}
          {mutation.isPending ? (
            <p className="text-xs text-muted-foreground">Analyzing analytics context…</p>
          ) : null}
        </div>

        <form onSubmit={onSubmit} className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a supply chain question…"
            className="h-11 flex-1 rounded-xl border border-border bg-background px-3 text-sm outline-none ring-offset-background focus:ring-2 focus:ring-ring"
          />
          <Button type="submit" disabled={mutation.isPending || !input.trim()}>
            Ask
          </Button>
        </form>
      </CardContent>
    </Card>
  );

  if (!floating) {
    return (
      <section className="space-y-6">
        <PageHeader pathname="/ai-insights" />
        <div className="mx-auto max-w-3xl">{panel}</div>
      </section>
    );
  }

  return (
    <div className="pointer-events-none fixed bottom-5 right-5 z-50 flex flex-col items-end gap-3">
      {open ? <div className="pointer-events-auto h-[34rem] w-[24rem] max-w-[calc(100vw-2rem)]">{panel}</div> : null}
      <Button
        className="pointer-events-auto size-14 rounded-full shadow-lg"
        onClick={() => setOpen((v) => !v)}
        aria-label="Toggle AI copilot"
      >
        <MessageCircle className="size-5" />
      </Button>
    </div>
  );
}
