export const storageKeys = {
  latestResumeRaw: "internmatch.resume.raw",
  latestResumeCandidate: "internmatch.resume.candidate",
  lastMatches: "internmatch.matches",
  lastTopK: "internmatch.topk",
  profile: "internmatch.profile",
};

export const saveJson = (key, value) => {
  localStorage.setItem(key, JSON.stringify(value));
};

export const loadJson = (key, fallback = null) => {
  try {
    const value = localStorage.getItem(key);
    if (!value) return fallback;
    return JSON.parse(value);
  } catch {
    return fallback;
  }
};
