export class Receiver {
    static connectionData: InMemoryConnectionData;
    /**
     * @param {number[]} messageByteArray
     */
    static sendCommand(messageByteArray: number[]): Uint8Array<any>;
    /**
     * @param {Int8Array} messageByteArray
     * @returns {Int8Array}
     */
    static heartBeat(messageByteArray: Int8Array): Int8Array;
    Receiver(): void;
}
import { InMemoryConnectionData } from '../../utils/connectionData/InMemoryConnectionData.js';
