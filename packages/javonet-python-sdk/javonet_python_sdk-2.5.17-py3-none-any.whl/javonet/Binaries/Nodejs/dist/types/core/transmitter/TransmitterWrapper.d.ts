export class TransmitterWrapper {
    static isNativeLibraryLoaded(): boolean;
    static loadNativeLibrary(): void;
    /**
     * @param {string} licenseKey
     */
    static activate(licenseKey: string): any;
    static sendCommand(messageArray: any): any;
    static setConfigSource(configSource: any): any;
    static setJavonetWorkingDirectory(path: any): void;
}
