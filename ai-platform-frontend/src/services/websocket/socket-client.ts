type MessageHandler = (
  event: MessageEvent
) => void;

class SocketClient {

  private socket:
    WebSocket | null = null;

  connect(
    url: string,
    onMessage?: MessageHandler
  ) {

    this.socket =
      new WebSocket(url);

    this.socket.onopen = () => {
      console.log(
        "WebSocket connected"
      );
    };

    this.socket.onmessage = (
      event
    ) => {

      if (onMessage) {
        onMessage(event);
      }
    };

    this.socket.onclose = () => {
      console.log(
        "WebSocket disconnected"
      );
    };

    this.socket.onerror = (
      error
    ) => {
      console.error(
        "WebSocket error",
        error
      );
    };
  }

  send(data: unknown) {

    if (
      this.socket &&
      this.socket.readyState ===
      WebSocket.OPEN
    ) {
      this.socket.send(
        JSON.stringify(data)
      );
    }
  }

  disconnect() {

    this.socket?.close();

    this.socket = null;
  }
}

export const socketClient =
  new SocketClient();