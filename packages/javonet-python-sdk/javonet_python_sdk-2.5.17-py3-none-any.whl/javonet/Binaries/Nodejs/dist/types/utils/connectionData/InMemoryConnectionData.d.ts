/**
 * @extends IConnectionData
 */
export class InMemoryConnectionData extends IConnectionData {
    _connectionType: 0;
    _hostname: string;
    get connectionType(): 0;
    get hostname(): string;
    serializeConnectionData(): number[];
    /**
     * @param {InMemoryConnectionData} other
     * @returns {boolean}
     */
    equals(other: InMemoryConnectionData): boolean;
}
import { IConnectionData } from './IConnectionData.js';
