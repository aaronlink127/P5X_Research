#if UNITY_EDITOR
using UnityEngine;
using UnityEditor;
using System.Collections.Generic;
using System.Linq;

public class P5XImportWindow : EditorWindow {
    public static List<Transform> GetTransformHierarchy(Transform rootTransform)
    {
        List<Transform> transformsList = new();
        
        AddTransforms(rootTransform, transformsList);

        return transformsList;
    }
    private static void AddTransforms(Transform parentTransform, List<Transform> list)
    {
        list.Add(parentTransform); // Add the current parent object

        // Iterate through all children of the current parent
        foreach (Transform childTransform in parentTransform)
        {
            // Recursively call the method for each child GameObject
            AddTransforms(childTransform, list);
        }
    }
    [MenuItem("Window/P5X Character Importer")]
    public static void OpenWindow()
    {
        var window = GetWindow<P5XImportWindow>();
        window.titleContent = new GUIContent("P5X Character Importer");
    }
    static readonly string[] qualities = {"High", "Lod", "Shadow"};
    private GameObject basePrefab;
    private List<GameObject> fashionPrefabs;
    private Vector2 scrollPos;
    private int quality = 0;
    private string statusText = "";
    private void OnGUI()
    {
        fashionPrefabs ??= new();
        quality = EditorGUILayout.Popup("Model Quality", quality, qualities);
        basePrefab = EditorGUILayout.ObjectField("Rig Prefab", basePrefab, typeof(GameObject), true) as GameObject;
        GUILayout.Label("Fashion Parts:");
        fashionPrefabs.RemoveAll(e=>e == null);
        for (int i = 0;i < fashionPrefabs.Count; i++) {
            fashionPrefabs[i] = EditorGUILayout.ObjectField($"Fashion Part {i+1}", fashionPrefabs[i], typeof(GameObject), true) as GameObject;
        }
        GameObject additionalPart = EditorGUILayout.ObjectField($"Fashion Part {fashionPrefabs.Count+1}", null, typeof(GameObject), true) as GameObject;
        if (additionalPart != null) {
            fashionPrefabs.Add(additionalPart);
        }
        bool enabled = basePrefab != null;
        GUI.enabled = enabled;
        if (GUILayout.Button("Add to Scene"))
        {
            statusText = "";
            
            GameObject newObj = basePrefab;
            if (PrefabUtility.IsPartOfPrefabAsset(newObj)) {
                statusText += $"Adding Main Rig {newObj.name}...\n";
                newObj = PrefabUtility.InstantiatePrefab(newObj) as GameObject;
            } else {
                statusText += $"Rig already in scene! {newObj.name}\n";
            }
            List<Transform> allTfs = GetTransformHierarchy(newObj.transform);
            foreach (GameObject fashion in fashionPrefabs) {
                GameObject fashionObj = fashion;
                if (PrefabUtility.IsPartOfPrefabAsset(fashionObj)) {
                    statusText += $"\tAdding Fashion {fashionObj.name}...\n";
                    fashionObj = PrefabUtility.InstantiatePrefab(fashionObj) as GameObject;
                } else {
                    statusText += $"\tFashion already in scene! {fashionObj.name}\n";
                }
                fashionObj.transform.parent = newObj.transform;
                foreach (MUActorMeshExportInfo exportInfo in fashionObj.GetComponentsInChildren<MUActorMeshExportInfo>()) {
                    GameObject obj = exportInfo.gameObject;
                    // statusText += fileToFilter(exportInfo.mHighMeshName);
                    string meshName = exportInfo.mHighMeshName;
                    string rootBoneName = exportInfo.mHighRootBoneName;
                    string[] boneNames = exportInfo.mHighMeshBoneNames;
                    Material[] meshMaterials = exportInfo.HighMeshMaterials;
                    if (quality == 1) {
                        meshName = exportInfo.mLODMeshName;
                        rootBoneName = exportInfo.mLodRootBoneName;
                        boneNames = exportInfo.mLodMeshBoneNames;
                        meshMaterials = exportInfo.mLodMaterials;
                    } else if (quality == 2) {
                        meshName = exportInfo.mShadowMeshName;
                        rootBoneName = exportInfo.mShadowRootBoneName;
                        boneNames = exportInfo.mShadowMeshBoneNames;
                        meshMaterials = exportInfo.mShadowMaterials;
                    }
                    statusText += $"\t\tProcessing {obj.name}...\n";
                    string assetPath = AssetDatabase.GetAllAssetPaths().FirstOrDefault(e=>e.EndsWith("/" + meshName));
                    if (assetPath != null && assetPath != "") {
                        Mesh newMesh = AssetDatabase.LoadAssetAtPath<Mesh>(assetPath) as Mesh;
                        if (!obj.TryGetComponent<SkinnedMeshRenderer>(out SkinnedMeshRenderer targetSkin))
                        {
                            targetSkin = obj.AddComponent<SkinnedMeshRenderer>();
                        }
                        targetSkin.sharedMesh = newMesh;
                        if (obj != null) {
                            statusText += $"\t\tAdding Skinned Mesh to {obj.name}...\n";
                            Transform[] newBones = new Transform[boneNames.Length];
                            int idx = 0;
                            foreach (string boneName in boneNames) {
                                Transform tst = allTfs.Find(e=>e.name == boneName);
                                if (tst != null) {
                                    if (boneName == rootBoneName) {
                                        targetSkin.rootBone = tst;
                                    }
                                    newBones[idx] = tst;
                                } else {
                                    statusText += "\t\t\tFailed to find: " + boneName + "\n";
                                }
                                idx += 1;
                            }
                            targetSkin.bones = newBones;
                            if (exportInfo.IsFaceMesh) {
                                targetSkin.SetMaterials(exportInfo.mFaceMaterials.ToList());
                            } else {
                                targetSkin.SetMaterials(meshMaterials.ToList());
                            }
                        }
                    } else {
                        statusText += $"\tFailed to find mesh {exportInfo.mHighMeshName}\n";
                    }
                }
            }
        }
        scrollPos = GUILayout.BeginScrollView(scrollPos);
        GUILayout.Label(statusText);
        GUILayout.EndScrollView();
    }
}
#endif