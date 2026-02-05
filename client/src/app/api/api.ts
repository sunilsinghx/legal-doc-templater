const API_BASE = process.env.NEXT_PUBLIC_API_URL;

async function handleResponse(res: Response) {
  let data: any;

  try {
    data = await res.json();
  } catch {
    throw new Error("Invalid server response");
  }

  if (!res.ok) {
    throw new Error(data?.detail || "Request failed");
  }

  return data;
}

export async function ingestFile(file: File) {
  const form = new FormData();
  form.append("file", file);

  const res: any = await fetch(`${API_BASE}/ingest`, {
    method: "POST",
    body: form,
  });

  return handleResponse(res);
}

export async function startDraft(query: string) {
  const res: any = await fetch(`${API_BASE}/start-draft`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  return handleResponse(res);
}

export async function finishDraft(payload: {
  template_id: number;
  answers: Record<string, string>;
  prefilled?: Record<string, string>;
}) {
  const res = await fetch(`${API_BASE}/finish-draft`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  return handleResponse(res);
}

export async function health() {
  const res = await fetch(`${API_BASE}/health`);
  return handleResponse(res);
}
