import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

async function proxy(request: NextRequest, paramsPromise: Promise<{ path: string[] }>) {
  const { path } = await paramsPromise;
  const backendUrl =
    process.env.INTERNAL_API_URL ||
    process.env.BACKEND_API_URL ||
    "http://127.0.0.1:8000";

  const targetPath = (path || []).join("/");
  const url = new URL(request.url);
  const targetUrl = `${backendUrl}/api/${targetPath}${url.search}`;

  const headers = new Headers(request.headers);
  headers.delete("host");

  try {
    const isBodyAllowed = request.method !== "GET" && request.method !== "HEAD";
    const body = isBodyAllowed ? await request.arrayBuffer() : undefined;

    const res = await fetch(targetUrl, {
      method: request.method,
      headers,
      body,
    });

    const responseHeaders = new Headers(res.headers);
    responseHeaders.delete("content-length");
    responseHeaders.delete("content-encoding");

    const resData = await res.arrayBuffer();

    return new NextResponse(resData, {
      status: res.status,
      statusText: res.statusText,
      headers: responseHeaders,
    });
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    console.error(`[API Proxy] Failed to proxy to ${targetUrl}:`, errorMsg);
    return NextResponse.json(
      {
        status: "unavailable",
        detail: {
          status: "unavailable",
          reason: `Cannot reach backend API service at ${backendUrl} (${errorMsg})`,
        },
      },
      { status: 503 }
    );
  }
}

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  return proxy(request, context.params);
}

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  return proxy(request, context.params);
}

export async function PUT(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  return proxy(request, context.params);
}

export async function DELETE(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  return proxy(request, context.params);
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    },
  });
}
