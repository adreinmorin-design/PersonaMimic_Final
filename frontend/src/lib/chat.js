const THOUGHT_PROCESS_REGEX = /<thought_process>([\s\S]*?)<\/thought_process>/i;

export function parseMessage(content = '') {
  const match = content.match(THOUGHT_PROCESS_REGEX);
  if (!match) {
    return { text: content, thought: null };
  }

  return {
    text: content.replace(THOUGHT_PROCESS_REGEX, '').trim(),
    thought: match[1].trim(),
  };
}

export function toChatHistory(messages = []) {
  return messages.map(({ role, content }) => ({
    role: role === 'bot' ? 'assistant' : role,
    content,
  }));
}
