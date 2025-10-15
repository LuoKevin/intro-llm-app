import { useState } from "react";

type ChatResponse = {
  answer: string;
  citations: Array<Record<string, unknown>>;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000"

export default function Home() {
    const [msg, setMsg] = useState("")
    const [answer, setAnswer] = useState<string | null>(null);
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    async function onAsk(e: React.FormEvent) {
        e.preventDefault()
        setLoading(true)
        setAnswer(null)
        setError(null)
        try {
            const url = new URL("/chat", API_BASE)
            url.searchParams.set("msg", msg)
            const res = await fetch(url.toString())
            if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
            const data = await res.json() as ChatResponse
            setAnswer(data.answer ?? "(no answer)")
        } catch (err:any) {
            setError(err.message ?? "request failed")
        } finally {
            setLoading(false)
        }
    }

    return (
        <main style={{ maxWidth: 720, margin: "40px auto", padding: 16, fontFamily: "system-ui"}}>
            <h1 style={{ fontSize: 24, marginBottom: 12}}>Minimal LLM Chat</h1>
            <form onSubmit={onAsk} style={{ display: "flex", gap: 8 }}>
                <input
                    type="text"
                    value={msg}
                    onChange={(e) => setMsg((e.target as HTMLInputElement).value)}
                    placeholder="Ask a question..."
                    style={{ flex: 1, padding: 10, border: "1px solid #ddd", borderRadius: 8}}
                    required
                />
                <button
                    type="submit"
                    disabled={loading || !msg.trim()}
                    style={{ padding: "10px 14px", borderRadius: 8, border: "1px solid #ccc", background: "#fafafa" }}
                >
                    {loading ? "Asking..." : "Ask"}
                </button>
            </form>

            {error && <p style={{ color: "crimson", marginTop: 12}}>Error: {error}</p>}
            {answer && (
                <div style={{ marginTop: 16, padding: 12, border: "1px solid #eee", borderRadius: 8, whiteSpace: "pre-wrap"}}>
                    {answer}
                </div>
            )}
        </main>
    );
}