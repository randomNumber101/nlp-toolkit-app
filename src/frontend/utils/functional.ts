// src/utils/functional.ts
const stringToStream = (str: string): ReadableStream<Uint8Array> => {
  const encoder = new TextEncoder();
  const uint8array = encoder.encode(str);

  return new ReadableStream({
    start(controller) {
      controller.enqueue(uint8array);
      controller.close();
    },
  });
};

export default stringToStream;
