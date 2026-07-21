async function parseError(response, fallback) {
  try {
    const data = await response.json();
    return data.detail || fallback;
  } catch {
    return fallback;
  }
}

export async function register(name, email, password) {
  const response = await fetch("/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password }),
  });
  if (!response.ok) {
    throw new Error(await parseError(response, "Registration failed"));
  }
  return response.json();
}

export async function login(email, password) {
  const response = await fetch("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ username: email, password }).toString(),
  });
  if (!response.ok) {
    throw new Error(await parseError(response, "Login failed"));
  }
  return response.json();
}
