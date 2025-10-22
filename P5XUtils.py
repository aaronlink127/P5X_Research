import sys
import os
import io
import struct

def getAssetHashCode(assetName: str):
    n = 0
    for i in assetName:
        n = ord(i) + 131*n
    return n & 0x7FFFFFFF
    
def buildBundleMap(gameDir: str):
    d = {}
    clientDir = os.path.join(gameDir,"client")
    outerPackageBundles = os.path.join(clientDir, "OuterPackage", "Bundles", "Windows")
    if os.path.isdir(outerPackageBundles):
        for numDir in os.listdir(outerPackageBundles):
            numPath = os.path.join(outerPackageBundles, numDir)
            if os.path.isdir(numPath):
                for bundleName in os.listdir(numPath):
                    d[bundleName] = os.path.join(numPath, bundleName)
    else:
        print("WARN: OuterPackage not found!")
    fileContOut = os.path.join(clientDir, "bin", "fileContentOut")
    if os.path.isdir(fileContOut):
        fileContBundles = os.path.join(fileContOut, "Bundles", "Windows")
        for numDir in os.listdir(fileContBundles):
            numPath = os.path.join(fileContBundles, numDir)
            if os.path.isdir(numPath):
                for bundleName in os.listdir(numPath):
                    if bundleName not in d:
                        d[bundleName] = os.path.join(numPath, bundleName)
    else:
        print("WARN: fileContentOut not found! It's recommended to run P5X_vFileContentExtract first!")
    return d

def readUInt32(f):
    return struct.unpack("<I", f.read(4))[0]

class ZeusAssetBundle:
    def __init__(self, name, deps):
        self.name = name
        self.deps = deps

class ZeusAssetManifest:
    def __init__(self):
        self.bundles = []
        self.bundleMap = {}

    def loadFromFB(self, filePath):
        f = io.open(filePath, "rb")
        f.seek(0x10, io.SEEK_SET)
        sLen = readUInt32(f)
        f.seek(sLen - 4, io.SEEK_CUR)
        assetCount = readUInt32(f)
        assetOffsets = []
        for i in range(assetCount):
            assetOffsets.append(f.tell() + readUInt32(f))
        for assetOffset in assetOffsets:
            f.seek(assetOffset, io.SEEK_SET)
            f.read(4)
            afterData = f.tell() + readUInt32(f)
            f.read(8)
            dependencies = []
            dependencyCount = readUInt32(f)
            for y in range(dependencyCount):
                dependencies.append(readUInt32(f))
            f.seek(afterData, io.SEEK_SET)
            bundleNameLen = readUInt32(f)
            bundleName = f.read(bundleNameLen).decode('utf-8')
            zeusBundle = ZeusAssetBundle(bundleName, dependencies)
            self.bundles.append(zeusBundle)
            self.bundleMap[bundleName] = zeusBundle
    
    def getManifestFromName(self, bundleName):
        if bundleName in self.bundleMap:
            return self.bundleMap[bundleName]
    
    def getDependencies(self, dep, dependencySet = None):
        if dependencySet is None:
            dependencySet = set()
        if dep.name not in dependencySet:
            dependencySet.add(dep.name)
            for subdep in dep.deps:
                self.getDependencies(self.bundles[subdep], dependencySet)
        return dependencySet

class AssetMap:
    def __init__(self):
        self.assetHashMap = {}
        self.assetNameMap = {}

    def getBundleByAsset(self, assetName: str):
        assetHash = getAssetHashCode(assetName)
        if assetHash in self.assetHashMap:
            return self.assetHashMap[assetHash]
        if assetName in self.assetNameMap:
            return self.assetNameMap[assetName]
    def loadFromFB(self, filePath):
        f = io.open(filePath, "rb")
        f.seek(0x10, io.SEEK_SET)
        sLen = readUInt32(f)
        f.seek(sLen - 4, io.SEEK_CUR)
        pathCount = readUInt32(f)
        assetPathOffsets = []
        for i in range(pathCount):
            assetPathOffsets.append(f.tell() + readUInt32(f))
        hashCount = readUInt32(f)
        assetHashOffsets = []
        for i in range(hashCount):
            assetHashOffsets.append(f.tell() + readUInt32(f))
        for pathOffset in assetPathOffsets:
            f.seek(pathOffset, io.SEEK_SET)
            f.read(4)
            assetNameOffs = f.tell() + readUInt32(f)
            f.read(4)
            bundleNameLen = readUInt32(f)
            bundleName = f.read(bundleNameLen).decode('utf-8')
            f.seek(assetNameOffs, io.SEEK_SET)
            assetNameLen = readUInt32(f)
            assetName = f.read(assetNameLen).decode('utf-8')
            self.assetNameMap[assetName] = bundleName
        for hashOffset in assetHashOffsets:
            f.seek(hashOffset, io.SEEK_SET)
            f.read(4)
            assetNameHash = readUInt32(f)
            extraDataLen = readUInt32(f)
            extraData = f.read(extraDataLen - 4)
            bundleNameLen = readUInt32(f)
            bundleName = f.read(bundleNameLen).decode('utf-8')
            self.assetHashMap[assetNameHash] = bundleName

def printUsage():
    print("Usage: python " + sys.argv[0] + " <path-to-game> <mode> [mode-args...]")
    print("Modes:")
    print("  find-asset <asset-name> - Prints bundle that contains asset")
    print("  find-asset-dep <asset-name> - Prints bundle that contains asset, and any dependencies")
    print("  find-bundle-dep <bundle-name> - Prints dependencies of a given bundle")

if len(sys.argv) > 2:
    bundleMap = buildBundleMap(sys.argv[1])
    assert "zeusBundleManifest.txt" in bundleMap, "bundle manifest couldn't be found"
    assert "assetMapName.txt" in bundleMap, "asset map couldn't be found"
    zeusManifest = ZeusAssetManifest()
    zeusManifest.loadFromFB(bundleMap["zeusBundleManifest.txt"])
    assetMap = AssetMap()
    assetMap.loadFromFB(bundleMap["assetMapName.txt"])

    def listBundleDeps(man, depth = 0, depSet = None):
        if depSet is None:
            depSet = set()
        if man.name not in depSet:
            depSet.add(man.name)
            print("  " * depth + man.name)
            for dep in man.deps:
                listBundleDeps(zeusManifest.bundles[dep], depth + 1, depSet)

    match sys.argv[2]:
        case "find-asset":
            assetName = sys.argv[3]
            bundleName = assetMap.getBundleByAsset(assetName)
            if bundleName is None:
                print("Couldn't find asset " + assetName)
            else:
                print(bundleName)
        case "find-bundle-dep":
            bundleName = sys.argv[3]
            bundleManifest = zeusManifest.getManifestFromName(bundleName)
            if bundleManifest is None:
                print("Couldn't find bundle " + bundleName)
            else:
                listBundleDeps(bundleManifest)
        case "find-asset-dep":
            assetName = sys.argv[3]
            bundleName = assetMap.getBundleByAsset(assetName)
            if bundleName is None:
                print("Couldn't find asset " + assetName)
            else:
                listBundleDeps(zeusManifest.getManifestFromName(bundleName))
        case _:
            print("Unknown command: " + sys.argv[2])
            printUsage()
else:
    print("Not enough args")
    printUsage()