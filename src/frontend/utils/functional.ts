// src/utils/functional.ts
export const stringToStream = (str: string): ReadableStream<Uint8Array> => {
  const encoder = new TextEncoder();
  const uint8array = encoder.encode(str);

  return new ReadableStream({
    start(controller) {
      controller.enqueue(uint8array);
      controller.close();
    },
  });
};


// src/utils/streamToString.ts

/**
 * Converts a ReadableStream of Uint8Array into a complete string.
 *
 * @param stream - The ReadableStream to convert.
 * @returns A Promise that resolves to the full string.
 */
export const streamToString = async (stream: ReadableStream<Uint8Array>): Promise<string> => {
  const reader = stream.getReader();
  const decoder = new TextDecoder('utf-8');
  let result = '';
  let done = false;

  while (!done) {
    const { value, done: doneReading } = await reader.read();
    done = doneReading;
    if (value) {
      result += decoder.decode(value, { stream: true });
    }
  }

  // Flush any remaining bytes
  result += decoder.decode();

  return result;
};

export function listToMap<T,S>(list: T[], key: (T) => S) : Record<S, T> {
  const newMap = {} as Record<S,T>
  list.forEach(e => newMap[key(e)] = e)
  return newMap
}

export default stringToStream;
