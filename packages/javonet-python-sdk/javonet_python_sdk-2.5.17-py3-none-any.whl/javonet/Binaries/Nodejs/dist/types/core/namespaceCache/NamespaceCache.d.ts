export class NamespaceCache {
    static _instance: null;
    namespaceCache: any[];
    cacheNamespace(namespaceRegex: any): void;
    isNamespaceCacheEmpty(): boolean;
    isTypeAllowed(typeToCheck: any): boolean;
    getCachedNamespaces(): any[];
    clearCache(): number;
}
