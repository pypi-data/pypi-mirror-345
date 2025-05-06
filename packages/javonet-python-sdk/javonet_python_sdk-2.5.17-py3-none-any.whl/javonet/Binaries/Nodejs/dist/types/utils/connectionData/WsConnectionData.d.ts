/**
 * Represents WebSocket connection data.
 * @extends IConnectionData
 */
export class WsConnectionData extends IConnectionData {
    /**
     * @param {string} hostname - The hostname of the connection.
     */
    constructor(hostname: string);
    /** @private @type {string} */
    private _hostname;
    /** @private @type {ConnectionType} */
    private _connectionType;
    /** @type {ConnectionType} */
    get connectionType(): {
        readonly IN_MEMORY: 0;
        readonly TCP: 1;
        readonly WEB_SOCKET: 2;
    };
    /** @type {string} */
    set hostname(value: string);
    /** @type {string} */
    get hostname(): string;
    /**
     * Serializes the connection data.
     * @returns {number[]} An array of connection data values.
     */
    serializeConnectionData(): number[];
    equals(other: any): boolean;
}
import { IConnectionData } from './IConnectionData.js';
