// localStorageSessions.js
// Utility for managing whiteboard session IDs in localStorage with TTL

const SESSIONS_KEY = "whiteboard_sessions";
const SESSION_TTL = 7 * 24 * 60 * 60 * 1000; // 1 week in ms

export function getSessions() {
  const raw = localStorage.getItem(SESSIONS_KEY);
  if (!raw) return [];
  try {
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

export function saveSessions(sessions) {
  localStorage.setItem(SESSIONS_KEY, JSON.stringify(sessions));
}

export function addOrUpdateSession(sessionId) {
  const now = Date.now();
  let sessions = getSessions();
  // Remove expired and duplicates
  sessions = sessions.filter(
    (s) => now - s.lastAccessed < SESSION_TTL && s.sessionId !== sessionId
  );
  // Add or update
  sessions.unshift({ sessionId, lastAccessed: now });
  saveSessions(sessions);
}

export function getRecentSessions() {
  const now = Date.now();
  return getSessions().filter((s) => now - s.lastAccessed < SESSION_TTL);
}

// Example usage:
// addOrUpdateSession("newSessionId");
// const recent = getRecentSessions();
