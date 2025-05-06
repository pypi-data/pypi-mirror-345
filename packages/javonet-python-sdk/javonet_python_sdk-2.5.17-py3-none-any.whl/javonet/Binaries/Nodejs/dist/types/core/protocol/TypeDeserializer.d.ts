export class TypeDeserializer {
    static deserializeCommand(encodedCommand: any): Command;
    static deserializeString(stringEncodingMode: any, encodedString: any): string;
    static deserializeInt(encodedInt: any): number;
    static deserializeBool(encodedBool: any): boolean;
    static deserializeFloat(encodedFloat: any): number;
    static deserializeByte(encodedByte: any): number;
    static deserializeChar(encodedChar: any): number;
    static deserializeLongLong(encodedLongLong: any): bigint;
    static deserializeDouble(encodedDouble: any): number;
    static deserializeULLong(encodedULLong: any): bigint;
    static deserializeUInt(encodedUInt: any): number;
    static deserializeNull(encodedNull?: null): null;
}
import { Command } from '../../utils/Command.js';
