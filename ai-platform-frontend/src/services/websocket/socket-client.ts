type SocketPayload = {
  type: string;
  content?: string;
};

type MessageHandler = (
  data: SocketPayload
) => void;
class SocketClient {

  private socket:
    WebSocket | null = null;

  private reconnectTimer:
    NodeJS.Timeout | null = null;

  private reconnectAttempts =
  0;

  private isConnected =
    false;

  private connectionState:
    "idle" |
    "connecting" |
    "connected" |
    "reconnecting" |
    "disconnected" |
    "failed"
  = "idle";

  private manuallyClosed =
  false;

  private messageQueue:
    string[] = [];

  private currentUrl:
    string | null = null;

  private heartbeatInterval:
    NodeJS.Timeout | null = null;

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

    this.connectionState =
      "connecting";

    this.socket =
      new WebSocket(url);

    this.socket.onopen = () => {

      this.isConnected = true;
      this.connectionState =
        "connected";
      this.reconnectAttempts = 0;
      this.startHeartbeat();

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

          try {

            this.socket?.send(
              message
            );

          } catch (error) {

          console.warn(
            "Queue flush failed",
            error
          );

          break;
         }
        }
      }
    };

    this.socket.onmessage = (
      event
    ) => {

     try {

      const data = JSON.parse(
        event.data
      );

      if (
        data.type === "pong"
      ) {
        return;
      }

      if (onMessage) {
        onMessage(data);
      }

    } catch (error) {

      console.warn(
        "Invalid websocket payload",
         error
      );
    }
  };

   this.socket.onclose = (
  event
) => {

  this.isConnected = false;

  if (
   this.heartbeatInterval
  ) {

   clearInterval(
     this.heartbeatInterval
   );

   this.heartbeatInterval =
     null;
  }

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

    this.connectionState =
      "failed";

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
   HEARTBEAT
========================= */

private startHeartbeat() {

  if (
    this.heartbeatInterval
  ) {
    return;
  }

  this.heartbeatInterval =
    setInterval(() => {

      if (
        this.socket?.readyState ===
        WebSocket.OPEN
      ) {

        try {

          this.socket.send(
            JSON.stringify({
              type: "ping",
            })
          );

        } catch (error) {

         console.warn(
           "Heartbeat failed",
          error
         );
       }
      }

    }, 30000);
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

    this.connectionState =
      "reconnecting";


    const delay = Math.min(
  1000 *
  Math.pow(
    2,
    this.reconnectAttempts
  ),
  30000
);

this.reconnectAttempts++;

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

      }, delay);
  }
  get status() {
   return this.connectionState;
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

    try {

      this.socket.send(
        payload
      );

    } catch (error) {

      console.warn(
        "WebSocket send failed",
        error
      );

      if (
        this.messageQueue.length >=
        100
      ) {

        this.messageQueue.shift();
      }

      this.messageQueue.push(
        payload
      );
    }

  } else {

    console.warn(
      "Socket unavailable. Queuing message."
    );

    if (
      this.messageQueue.length >=
      100
    ) {

      this.messageQueue.shift();
    }

    this.messageQueue.push(
      payload
    );
  }
}

  /* =========================
     DISCONNECT
  ========================= */

  disconnect() {

  if (
    this.socket?.readyState ===
    WebSocket.CONNECTING
  ) {
    return;
  }

  this.manuallyClosed = true;

  if (
    this.reconnectTimer
  ) {

    clearTimeout(
      this.reconnectTimer
    );

    this.reconnectTimer =
      null;
  }

  if (
    this.heartbeatInterval
  ) {

    clearInterval(
      this.heartbeatInterval
    );

    this.heartbeatInterval =
      null;
  }

  if (
    this.socket &&
    this.socket.readyState !==
    WebSocket.CLOSED
  ) {

    this.socket.close();
  }

  this.socket = null;

  this.isConnected = false;

  this.connectionState =
    "disconnected";
  }
}

export const socketClient =
  new SocketClient();