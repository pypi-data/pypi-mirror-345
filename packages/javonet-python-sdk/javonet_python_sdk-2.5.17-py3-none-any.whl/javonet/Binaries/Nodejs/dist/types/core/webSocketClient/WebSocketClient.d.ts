/**
 * WebSocketClient class that handles WebSocket connection, message sending, and automatic disconnection.
 */
export class WebSocketClient {
    /**
     * @param {string} url
     * @param {object} options
     */
    constructor(url: string, options: object);
    /**
     * @type {string}
     */
    url: string;
    /**
     * @type {WebSocket | null}
     */
    instance: WebSocket | null;
    /**
     * @type {boolean} isConnected indicates whether the WebSocket is connected.
     */
    isConnected: boolean;
    /**
     * @type {boolean}
     */
    isDisconnectedAfterMessage: boolean;
    /**
     * Connects to the WebSocket server.
     * @async
     * @returns {Promise<WebSocket>} - A promise that resolves when the connection is established.
     */
    connect(): Promise<WebSocket>;
    /**
     * Sends messageArray through websocket connection
     * @async
     * @param {Buffer|ArrayBuffer|Buffer[]} messageArray
     * @returns {Promise<Buffer|ArrayBuffer|Buffer[]>}
     */
    send(messageArray: Buffer | ArrayBuffer | Buffer[]): Promise<Buffer | ArrayBuffer | Buffer[]>;
    /**
     * Disconnects the WebSocket by terminating the connection.
     */
    disconnect(): void;
    /**
     * Connects to the WebSocket server.
     * @private
     * @async
     * @returns {Promise<WebSocket>} - A promise that resolves when the connection is established.
     */
    private _connect;
}
