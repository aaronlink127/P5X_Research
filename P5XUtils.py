import sys
import os
import io
import struct
from io import StringIO, BytesIO
import shlex

def getAssetHashCode(assetName: str):
    n = 0
    for i in assetName:
        n = ord(i) + 131*n
    return n & 0x7FFFFFFF
    
def getBundleObfusOffset(name):
    return (getAssetHashCode(name) & 0x1F) + 8

def readInt32(f):
    return struct.unpack("<i", f.read(4))[0]

def readUInt32(f):
    return struct.unpack("<I", f.read(4))[0]

def openBytes(s, mode):
    if "b" in mode:
        return BytesIO(s)
    else:
        return StringIO(s.decode('cp1252'))

class IFile:
    def readAllBytes(self):
        with self.open("rb") as f:
            return f.read()

class RealFile(IFile):
    def __init__(self, path):
        self.path = path

    def readAllBytes(self):
        root, ext = os.path.splitext(self.path)
        if ext == ".bundle":
            baseName = os.path.basename(self.path)
            with open(self.path, "rb") as f:
                f.seek(getBundleObfusOffset(baseName), io.SEEK_SET)
                return f.read()
        return IFile.readAllBytes(self)

    def open(self, mode):
        root, ext = os.path.splitext(self.path)
        if ext == ".bundle":
            baseName = os.path.basename(self.path)
            with open(self.path, "rb") as f:
                f.seek(getBundleObfusOffset(baseName), io.SEEK_SET)
                return openBytes(f.read(), mode)
        else:
            return io.open(self.path, mode)

class VFile(IFile):
    def __init__(self, srcfs, idx, size, pos):
        self.srcfs = srcfs
        self.idx = idx
        self.size = size
        self.pos = pos
    
    def readAllBytes(self):
        vContentPath = os.path.join(self.srcfs.root, "_vfileContent" + str(self.idx))
        with io.open(vContentPath, "rb") as f:
            f.seek(self.pos, io.SEEK_SET)
            return f.read(self.size)

    def open(self, mode):
        allBytes = self.readAllBytes()
        return openBytes(allBytes, mode)

class RealFSMount:
    def __init__(self, root):
        self.root = root
    def getFile(self, path):
        realpath = os.path.join(self.root, path)
        if os.path.exists(realpath):
            return RealFile(realpath)

class VFSMount:
    def __init__(self, root):
        self.root = root
        self.map = {}
        indexFb = os.path.join(root, "_vfileIndexV2.fb")
        with io.open(indexFb, "rb") as f:
            f.seek(f.tell() + readUInt32(f), io.SEEK_SET)
            f.read(4)
            f.seek(f.tell() + readUInt32(f), io.SEEK_SET)
            numContentChunks = readUInt32(f)
            chunkDataPos = []
            for i in range(numContentChunks):
                chunkDataPos.append(f.tell() + readInt32(f))
            for i in range(numContentChunks):
                offset = chunkDataPos[i]
                f.seek(offset, io.SEEK_SET)
                f.read(4)
                sectionEnd = f.tell() + readInt32(f)
                f.seek(f.tell() + readInt32(f), io.SEEK_SET)
                numEntries = readUInt32(f)
                entries = []
                for x in range(numEntries):
                    entries.append(f.tell() + readUInt32(f))
                for entryPos in entries:
                    f.seek(entryPos, io.SEEK_SET)
                    # print(hex(entryPos))
                    f.read(4)
                    entryMetaEnd = f.tell() + readUInt32(f)
                    fileSize = readUInt32(f)
                    fileOffset = readUInt32(f)
                    f.seek(entryMetaEnd, io.SEEK_SET)
                    filePathLen = readUInt32(f)
                    filePath = f.read(filePathLen).decode("utf-8")
                    baseName = os.path.basename(filePath)
                    root, ext = os.path.splitext(baseName)
                    if ext == ".bundle":
                        fileOffset = fileOffset + getBundleObfusOffset(baseName)
                    self.map[filePath] = VFile(self, i, fileSize, fileOffset)

    def getFile(self, path):
        if path in self.map:
            return self.map[path]

class VFileSystem:
    def __init__(self, gameDir):
        self.mounts = []
        self.mounts.append(RealFSMount(os.path.join(gameDir, "client", "OuterPackage")))
        self.mounts.append(VFSMount(os.path.join(gameDir, "client", "bin")))
        self.mounts.append(RealFSMount(os.path.join(gameDir, "client", "bin")))
        # self.mounts.append(RealFSMount(os.path.join(gameDir, "client", "bin", "fileContentOut")))

    def exists(self, path):
        fp = self.getFile(path)
        return fp is not None

    def open(self, path, mode):
        f = self.getFile(path)
        if f is not None:
            return f.open(mode)

    def readAllBytes(self, path):
        f = self.getFile(path)
        if f is not None:
            return f.readAllBytes()

    def getFile(self, path):
        for m in self.mounts:
            g = m.getFile(path)
            if g is not None:
                return g
    
def getBundlePath(abName):
    return "Bundles/Windows/" + str(getAssetHashCode(abName) % 200).zfill(3) + "/" + abName

def printCmds():
    print("Commands:")
    print("  help - Show this message")
    print("  exit - Exit this utility")
    print("  find-asset <asset-name> - Prints bundle that contains asset")
    print("  find-asset-dep <asset-name> - Prints bundle that contains asset, and any dependencies")
    print("  find-bundle-dep <bundle-name> - Prints dependencies of a given bundle")
    print("  extract-bundle <bundle-name> <output-dir> - Extracts bundle to directory")
    print("  extract-bundle-dep <bundle-name> <output-dir> - Extracts bundle dependency tree to directory")
    print("  extract-asset-dep <asset-name> <output-dir> - Extracts bundle dependency tree of asset to directory")

def verifyGamePath(path):
    return os.path.exists(os.path.join(path, "client"))
vfs = None
if len(sys.argv) < 2:
    while vfs is None:
        try:
            gamePath = input("Game Path: ")
        except KeyboardInterrupt as e:
            exit()
        if verifyGamePath(gamePath):
            try:
                vfs = VFileSystem(gamePath)
            except Exception as e:
                print(e)
        else:
            print("The path provided doesn't seem to be a P5X install!")
else:
    if verifyGamePath(sys.argv[1]):
        try:
            vfs = VFileSystem(sys.argv[1])
        except Exception as e:
            print(e)
            exit()
    else:
        print("The path provided doesn't seem to be a P5X install!")
        exit()

class ZeusAssetBundle:
    def __init__(self, name, deps):
        self.name = name
        self.deps = deps

class ZeusAssetManifest:
    def __init__(self):
        self.bundles = []
        self.bundleMap = {}

    def loadFromFB(self, filePath):
        with vfs.open(filePath, "rb") as f:
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
        with vfs.open(filePath, "rb") as f:
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


zeusManifest = ZeusAssetManifest()
zeusManifest.loadFromFB(getBundlePath("zeusBundleManifest.txt"))
assetMap = AssetMap()
assetMap.loadFromFB(getBundlePath("assetMapName.txt"))

def ensureOutDirectory(outDir):
    if not os.path.exists(outDir):
        os.makedirs(outDir)
    if not os.path.isdir(outDir):
        raise Exception("\"" + outDir + "\" exists, but is a file, not a folder.")
    return outDir

def listBundleDeps(man, depth = 0, depSet = None):
    if depSet is None:
        depSet = set()
    if man.name not in depSet:
        depSet.add(man.name)
        print("  " * depth + man.name)
        for dep in man.deps:
            listBundleDeps(zeusManifest.bundles[dep], depth + 1, depSet)

def runCommand(cmd, args):
    match cmd:
        case "find-asset":
            assetName = args[0]
            bundleName = assetMap.getBundleByAsset(assetName)
            if bundleName is None:
                print("Couldn't find asset " + assetName)
            else:
                print(bundleName)
        case "find-bundle-dep":
            bundleName = args[0]
            bundleManifest = zeusManifest.getManifestFromName(bundleName)
            if bundleManifest is None:
                print("Couldn't find bundle " + bundleName)
            else:
                listBundleDeps(bundleManifest)
        case "find-asset-dep":
            assetName = args[0]
            bundleName = assetMap.getBundleByAsset(assetName)
            if bundleName is None:
                print("Couldn't find asset " + assetName)
            else:
                listBundleDeps(zeusManifest.getManifestFromName(bundleName))
        case "extract-bundle":
            bundleName = args[0]
            outDir = ensureOutDirectory(args[1].strip("\"\'"))
            bundleManifest = zeusManifest.getManifestFromName(bundleName)
            if bundleManifest is None:
                print("Couldn't find bundle " + bundleName)
            else:
                allBytes = vfs.readAllBytes(getBundlePath(bundleName))
                with open(os.path.join(outDir, bundleName), "wb") as f:
                    f.write(allBytes)
        case "extract-bundle-dep":
            bundleName = args[0]
            outDir = ensureOutDirectory(args[1].strip("\"\'"))
            bundleManifest = zeusManifest.getManifestFromName(bundleName)
            if bundleManifest is None:
                print("Couldn't find bundle " + bundleName)
            else:
                deps = zeusManifest.getDependencies(bundleManifest)
                for dep in deps:
                    allBytes = vfs.readAllBytes(getBundlePath(dep))
                    with open(os.path.join(outDir, dep), "wb") as f:
                        f.write(allBytes)
        case "extract-asset-dep":
            assetName = args[0]
            outDir = ensureOutDirectory(args[1].strip("\"\'"))
            bundleName = assetMap.getBundleByAsset(assetName)
            if bundleName is None:
                print("Couldn't find asset " + assetName)
            else:
                deps = zeusManifest.getDependencies(zeusManifest.getManifestFromName(bundleName))
                for dep in deps:
                    allBytes = vfs.readAllBytes(getBundlePath(dep))
                    with open(os.path.join(outDir, dep), "wb") as f:
                        f.write(allBytes)
        case "exit":
            exit()
        case "help":
            printCmds()
        case _:
            print("Unknown command: " + cmd + ". Use help to see all commands.")

if len(sys.argv) < 3:
    while True:
        try:
            cmd = input("> ")
        except KeyboardInterrupt as e:
            exit()
        args = shlex.split(cmd, posix=False)
        try:
            runCommand(args[0], args[1:])
        except Exception as e:
            print("An error occurred while executing a command.")
            print(e)
else:
    runCommand(sys.argv[2], sys.argv[3:])