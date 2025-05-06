export class Interpreter {
    handler: any;
    /**
     *
     * @param {Command} command
     * @param {IConnectionData} connectionData
     * @returns
     */
    executeAsync(command: Command, connectionData: IConnectionData): Promise<import("../../utils/Command.js").Command>;
    /**
     *
     * @param {Command} command
     * @param {WsConnectionData} connectionData
     * @returns {Promise<Command>}
     */
    execute(command: Command, connectionData: WsConnectionData): Promise<Command>;
    /**
     *
     * @param {number[]} messageByteArray
     * @returns {Command}
     */
    process(messageByteArray: number[]): Command;
}
export type Receiver = import("../receiver/Receiver.js").Receiver;
export type Transmitter = import("../transmitter/Transmitter.js").Transmitter;
export type TransmitterWebsocket = import("../transmitter/TransmitterWebsocket.js").TransmitterWebsocket;
export type TransmitterWebsocketBrowser = import("../transmitter/TransmitterWebsocketBrowser.js").TransmitterWebsocketBrowser;
