type MessageHandler = (
  event: MessageEvent
) => void;

class SocketClient {

  private socket:
    WebSocket | null = null;

  private reconnectTimer:
    NodeJS.Timeout | null = null;

  private isConnected =
    false;

  private manuallyClosed =
  false;

  private messageQueue:
    string[] = [];

  private currentUrl:
    string | null = null;

  private currentHandler:
    MessageHandler | undefined;

  connect(
    url: string,
    onMessage?: MessageHandler
  ) {

    if (
      this.socket &&
      (
        this.socket.readyState ===
          WebSocket.OPEN ||

        this.socket.readyState ===
          WebSocket.CONNECTING
      )
    ) {
      return;
    }

    this.currentUrl = url;

    this.currentHandler =
      onMessage;

    this.manuallyClosed =
     false;  

    this.socket =
      new WebSocket(url);

    this.socket.onopen = () => {

      this.isConnected = true;

      console.log(
        "WebSocket connected"
      );

      /* =========================
         FLUSH QUEUE
      ========================= */

      while (
        this.messageQueue.length > 0
      ) {

        const message =
          this.messageQueue.shift();

        if (message) {

          this.socket?.send(
            message
          );
        }
      }
    };

    this.socket.onmessage = (
      event
    ) => {

      if (onMessage) {
        onMessage(event);
      }
    };

   this.socket.onclose = (
  event
) => {

  this.isConnected = false;

  console.log(
    "WebSocket disconnected",
    event.code
  );

  /* =========================
     AUTH FAILURE
  ========================= */

  if (
    event.code === 1008
  ) {

    console.warn(
      "WebSocket auth failed"
    );

    return;
  }

  /* =========================
     AUTO RECONNECT
  ========================= */

  if (
    !this.manuallyClosed
  ) {

    this.reconnect();
  }
};

    this.socket.onerror = (
      error
    ) => {

      console.warn(
        "WebSocket warning",
        error
      );
    };
  }

  /* =========================
     AUTO RECONNECT
  ========================= */

  private reconnect() {

    if (
      this.reconnectTimer
    ) {
      return;
    }

    this.reconnectTimer =
      setTimeout(() => {

        console.log(
          "Reconnecting websocket..."
        );

        if (
          this.currentUrl
        ) {

          this.connect(
            this.currentUrl,
            this.currentHandler
          );
        }

        this.reconnectTimer =
          null;

      }, 3000);
  }

  /* =========================
     SEND MESSAGE
  ========================= */

  send(data: unknown) {

    const payload =
      JSON.stringify(data);

    if (
      this.socket &&
      this.socket.readyState ===
      WebSocket.OPEN
    ) {

      this.socket.send(
        payload
      );

    } else {

      console.warn(
        "Socket unavailable. Queuing message."
      );

      this.messageQueue.push(
        payload
      );
    }
  }

  /* =========================
     DISCONNECT
  ========================= */

  disconnect() {

    this.manuallyClosed =
      true;

    this.socket?.close();

    this.socket = null;

    this.isConnected = false;
  }
}

export const socketClient =
  new SocketClient();