/**
 * Cloudflare Pages：将同域 POST/OPTIONS /api/draw 转发到 Vercel 上的 FastAPI。
 * 静态托管层对 POST 会 405；走 Function 后由上游处理。
 *
 * 可选：Pages → Settings → 环境变量 API_ORIGIN（无末尾斜杠），默认如下。
 */
const DEFAULT_ORIGIN = 'https://aujourdhui-open0319.vercel.app';

export async function onRequest(context) {
  const { request, env } = context;
  const origin = String(env.API_ORIGIN || DEFAULT_ORIGIN).replace(/\/$/, '');
  const u = new URL(request.url);
  const target = `${origin}${u.pathname}${u.search}`;

  const headers = new Headers(request.headers);
  headers.delete('host');

  return fetch(target, {
    method: request.method,
    headers,
    body: request.body,
    redirect: 'follow',
  });
}
