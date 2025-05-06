export class TransmitterWebsocket {
    /**
     * @returns {void}
     */
    static initialize(): void;
    /**
     * @returns {void}
     */
    static setConfigSource(): void;
    /**
     * @returns {void}
     */
    static activate(): void;
    /**
     * @async
     * @param {number[]} messageByteArray
     * @param {WsConnectionData} connectionData
     * @returns {Promise<number[]>} responseByteArray
     */
    static sendCommand(messageByteArray: number[], connectionData: WsConnectionData): Promise<number[]>;
}
