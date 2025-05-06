export class CommandDeserializer {
    constructor(buffer: any);
    buffer: any;
    command: Command;
    position: number;
    /**
     * @returns {Command}
     */
    deserialize(): Command;
    isAtEnd(): boolean;
    readObject(typeNum: any): string | number | bigint | boolean | Command | (() => bigint) | null;
    readCommand(): Command;
    readString(): string;
    readInt(): number;
    readBool(): boolean;
    readFloat(): number;
    readByte(): number;
    readChar(): number;
    readLongLong(): bigint;
    readDouble(): number;
    readUllong(): bigint;
    readUInt(): number;
    readNull(): null;
}
import { Command } from '../../utils/Command.js';
