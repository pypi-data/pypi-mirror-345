/**
 * @typedef {object} ConnectionData
 * @property {string} hostname
 */
export class TransmitterWebsocketBrowser {
    /**
     * @returns {void}
     */
    static initialize(): void;
    /**
     * @returns {void}
     */
    static activate(): void;
    /**
     * @async
     * @param {Int8Array} messageByteArray
     * @param {ConnectionData} connectionData
     * @returns {Promise<Int8Array>} responseByteArray
     */
    static sendCommand(messageByteArray: Int8Array, connectionData: ConnectionData): Promise<Int8Array>;
    /**
     * @async
     * @param {any} configSource
     * @returns {void}
     */
    static setConfigSource(configSource: any): void;
}
export type ConnectionData = {
    hostname: string;
};
