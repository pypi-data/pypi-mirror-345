export class CommandSerializer {
    serialize(rootCommand: any, connectionData: any): Uint8Array<any>;
    serializeRecursively(command: any, buffers: any): void;
}
