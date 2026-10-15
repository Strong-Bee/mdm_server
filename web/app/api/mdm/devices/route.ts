import { NextRequest, NextResponse } from "next/server";
import type { DevicesResponse } from "@/lib/mdm-types";

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

export async function GET(request: NextRequest) {
  const base = backendUrl();
  const token = request.headers.get("x-mdm-admin-token");
  if (!base) return NextResponse.json({ error: "MDM_API_BASE_URL belum dikonfigurasi atau bukan URL HTTPS yang valid." }, { status: 503 });
  if (!token || token.length < 16) return NextResponse.json({ error: "Token admin tidak valid." }, { status: 401 });

  try {
    const upstream = await fetch(`${base}/api/devices`, {
      headers: { Authorization: `Bearer ${token}`, Accept: "application/json" },
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
    });
    const body = (await upstream.json().catch(() => ({ error: "Respons backend tidak valid." }))) as DevicesResponse | { error: string };
    return NextResponse.json(body, { status: upstream.status, headers: { "Cache-Control": "no-store" } });
  } catch {
    return NextResponse.json({ error: "Backend MDM tidak dapat dijangkau." }, { status: 502 });
  }
}
