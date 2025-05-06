export class TypeCache {
    static _instance: null;
    typeCache: any[];
    cacheType(typRegex: any): void;
    isTypeCacheEmpty(): boolean;
    isTypeAllowed(typeToCheck: any): boolean;
    getCachedTypes(): any[];
    clearCache(): number;
}
