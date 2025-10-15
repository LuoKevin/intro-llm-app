import { useRef, useState } from "react";

type ChatResponse = {
  answer: string;
  citations: Array<Record<string, unknown>>;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000"

export default function Home() {
    const [msg, setMsg] = useState("")
    const [answer, setAnswer] = useState<string>("");
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null) 
    const esRef = useRef<EventSource | null>(null)

    async function onAsk(e: React.FormEvent) {
        e.preventDefault()
        setLoading(true)
        setAnswer("")
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

    function onStream() {
        setError(null)
        setAnswer("")
        //Close any prior stream
        esRef.current?.close()

        const url = new URL("/chat/stream", API_BASE)
        url.searchParams.set("msg", msg)
        const es = new EventSource(url.toString())
        esRef.current = es

        es.onmessage = (evt) => {
            const payload = evt.data as string

            if (payload == "[DONE]") {
                es.close()
                esRef.current = null
                return
            }

            // Citations arrive as a final JSON frame, append nothing to text
            if (payload.startsWith("{")) {
                const obj = JSON.parse(payload)
                return
            }

            setAnswer((prev) => prev + payload)
        }

        es.onerror = () => {
            setError("stream error")
            es.close()
            esRef.current = null
        }
    }

    function stopStream() {
        esRef.current?.close()
        esRef.current = null
    }

    return (
        <main style={{ maxWidth: 720, margin: "40px auto", padding: 16, fontFamily: "system-ui"}}>
            <h1 style={{ fontSize: 24, marginBottom: 12}}>Minimal LLM Chat</h1>
            <form onSubmit={onAsk} style={{ display: "flex", gap: 8, marginBottom: 8 }}>
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

                <button
                    type="button" 
                    onClick={onStream} 
                    disabled={!msg.trim()} 
                    style={{ padding: "10px 14px", borderRadius: 8 }}
                >
                    Stream
                </button>
                <button 
                    type="button" 
                    onClick={stopStream}
                    style={{ padding: "10px 14px", borderRadius: 8 }}
                >
                    Stop
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