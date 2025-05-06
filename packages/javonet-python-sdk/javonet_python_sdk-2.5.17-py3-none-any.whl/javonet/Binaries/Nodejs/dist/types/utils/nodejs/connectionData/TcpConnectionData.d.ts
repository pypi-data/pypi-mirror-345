/**
 * @extends IConnectionData
 */
export class TcpConnectionData extends IConnectionData {
    constructor(hostname: any, port: any);
    _port: any;
    _hostname: any;
    _connectionType: 1;
    ipAddress: string | null;
    get connectionType(): 1;
    get hostname(): any;
    /**
     * @param {TcpConnectionData} other
     * @returns {boolean}
     */
    equals(other: TcpConnectionData): boolean;
    /**
     * @param {string} hostname
     * @returns {string|null}
     */
    resolveIpAddress(hostname: string): string | null;
    serializeConnectionData(): 1[];
    #private;
}
import { IConnectionData } from '../../connectionData/IConnectionData.js';
