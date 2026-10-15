import { NextRequest, NextResponse } from "next/server";
import type { QueueCommandRequest, QueueCommandResponse } from "@/lib/mdm-types";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function backendUrl(): string | null {
  const base = process.env.MDM_API_BASE_URL?.trim();
  if (!base) return null;
  try {
    const url = new URL(base);
    if (url.protocol !== "https:" && url.hostname !== "localhost" && url.hostname !== "127.0.0.1") return null;
    return url.toString().replace(/\/$/, "");
  } catch {
    return null;
  }
}

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ udid: string }> },
) {
  const base = backendUrl();
  const token = request.headers.get("x-mdm-admin-token");
  if (!base) return NextResponse.json({ error: "MDM_API_BASE_URL belum dikonfigurasi atau bukan URL HTTPS yang valid." }, { status: 503 });
  if (!token || token.length < 16) return NextResponse.json({ error: "Token admin tidak valid." }, { status: 401 });

  let input: QueueCommandRequest;
  try {
    input = (await request.json()) as QueueCommandRequest;
  } catch {
    return NextResponse.json({ error: "Body JSON tidak valid." }, { status: 400 });
  }
  // The backend remains the source of truth for the complete Apple command schema.
  if (!input || typeof input.command_type !== "string") {
    return NextResponse.json({ error: "command_type wajib diisi." }, { status: 400 });
  }
  if (input.payload !== undefined && (typeof input.payload !== "object" || input.payload === null || Array.isArray(input.payload))) {
    return NextResponse.json({ error: "payload harus berupa objek JSON." }, { status: 400 });
  }

  const { udid } = await context.params;
  try {
    const upstream = await fetch(`${base}/api/devices/${encodeURIComponent(udid)}/commands`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(input),
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
    });
    const body = (await upstream.json().catch(() => ({ error: "Respons backend tidak valid." }))) as QueueCommandResponse | { error: string };
    return NextResponse.json(body, { status: upstream.status, headers: { "Cache-Control": "no-store" } });
  } catch {
    return NextResponse.json({ error: "Backend MDM tidak dapat dijangkau." }, { status: 502 });
  }
}
