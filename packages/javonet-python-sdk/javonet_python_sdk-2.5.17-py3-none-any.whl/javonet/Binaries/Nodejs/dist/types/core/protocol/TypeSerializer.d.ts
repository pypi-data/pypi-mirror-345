export class TypeSerializer {
    static serializePrimitive(payload_item: any): Buffer<ArrayBuffer>;
    static serializeCommand(command: any): Buffer<ArrayBuffer>;
    static serializeString(string_value: any): Buffer<ArrayBuffer>;
    static serializeInt(int_value: any): Buffer<ArrayBuffer>;
    static serializeBool(bool_value: any): Buffer<ArrayBuffer>;
    static serializeFloat(float_value: any): Buffer<ArrayBuffer>;
    static serializeByte(byte_value: any): Buffer<ArrayBuffer>;
    static serializeChar(char_value: any): Buffer<ArrayBuffer>;
    static serializeLongLong(longlong_value: any): Buffer<ArrayBuffer>;
    static serializeDouble(double_value: any): Buffer<ArrayBuffer>;
    static serializeULLong(ullong_value: any): Buffer<ArrayBuffer>;
    static serializeUInt(uint_value: any): Buffer<ArrayBuffer>;
    static serializeNull(): Buffer<ArrayBuffer>;
    static serializeIntValue(int_value: any): Buffer<ArrayBuffer>;
}
import { Buffer } from 'buffer';
