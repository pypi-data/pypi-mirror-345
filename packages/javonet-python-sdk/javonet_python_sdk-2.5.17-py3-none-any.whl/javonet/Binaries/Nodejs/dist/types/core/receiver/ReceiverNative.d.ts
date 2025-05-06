export class ReceiverNative {
    static sendCommand(messageByteArray: any): Uint8Array<any>;
    static heartBeat(messageByteArray: any): Int8Array<ArrayBufferLike>;
}
