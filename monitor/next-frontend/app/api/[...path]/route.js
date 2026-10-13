async function proxy(request, { params }) {
  const base = process.env.MONITOR_API_URL;
  if (!base) {
    return Response.json({ message: "감시 API 주소가 설정되지 않았습니다." }, { status: 503 });
  }

  const { path } = await params;
  const incoming = new URL(request.url);
  const upstream = new URL(`/api/${path.map(encodeURIComponent).join("/")}${incoming.search}`, `${base.replace(/\/$/, "")}/`);
  const headers = new Headers();
  for (const name of ["cookie", "x-csrf-token", "content-type", "accept"]) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }

  try {
    const response = await fetch(upstream, {
      method: request.method,
      headers,
      body: ["GET", "HEAD"].includes(request.method) ? undefined : await request.arrayBuffer(),
      cache: "no-store",
      redirect: "manual",
    });
    const returned = new Headers();
    for (const name of ["content-type", "location"]) {
      const value = response.headers.get(name);
      if (value) returned.set(name, value);
    }
    for (const cookie of response.headers.getSetCookie()) returned.append("set-cookie", cookie);
    returned.set("cache-control", "no-store");
    const body = [204, 205, 304].includes(response.status) ? null : await response.arrayBuffer();
    return new Response(body, { status: response.status, headers: returned });
  } catch {
    return Response.json({ message: "감시 API에 연결하지 못했습니다. 잠시 후 다시 불러와 주세요." }, { status: 502 });
  }
}

export { proxy as GET, proxy as POST, proxy as PUT, proxy as PATCH, proxy as DELETE };
