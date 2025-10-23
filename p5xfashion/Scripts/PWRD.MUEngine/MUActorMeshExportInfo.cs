using UnityEngine;
using System.Collections.Generic;
using System;

// Namespace: MUEngine
public enum EFacePart // TypeDefIndex: 5205
{
    NotFacePart = -1,
    Eyeball = 1,
    SpEyeball = 2,
    Eyelid = 3,
    Beard = 4,
    Tear = 5,
    Cheek = 6
}
public class MUActorMeshExportInfo : MonoBehaviour
{
	// Fields
	public bool IsFaceMesh; // 0x20
	public EFacePart FacePart; // 0x24
	[SerializeField]
	public string mHighRootBoneName; // 0x28
	[SerializeField]
	public string mLodRootBoneName; // 0x30
	[SerializeField]
	public string mShadowRootBoneName; // 0x38
	[SerializeField]
	public string[] mHighMeshBoneNames; // 0x40
	[SerializeField]
	public string[] mLodMeshBoneNames; // 0x48
	[SerializeField]
	public string[] mShadowMeshBoneNames; // 0x50
	[SerializeField]
	public Material[] mHighMeshMaterials; // 0x58
	[SerializeField]
	public Mesh mMesh; // 0x60
	[SerializeField]
	public Mesh mLODMesh; // 0x68
	[SerializeField]
	public Mesh mShadowMesh; // 0x70
	[SerializeField]
	public string mHighMeshName; // 0x78
	[SerializeField]
	public string mLODMeshName; // 0x80
	[SerializeField]
	public string mShadowMeshName; // 0x88
	[SerializeField]
	public Material[] mLodMaterials; // 0x90
	[SerializeField]
	public Material[] mShadowMaterials; // 0x98
	[SerializeField]
	public bool mIsSkinnedMeshRender; // 0xA0
	[SerializeField]
	public string mMakeFaceTemplateName; // 0xA8
	[SerializeField]
	public string mMakeFaceTexTemplateName; // 0xB0
	[SerializeField]
	public MUActorSkelMeshDesc[] MeshList; // 0xB8
	[SerializeField]
	public Material[] mFaceMaterials; // 0xC0

	// Properties
	public string HighRootBoneName { get; set; }
	public string LodRootBoneName { get; set; }
	public string ShadowRootBoneName { get; set; }
	public Material[] HighMeshMaterials { get; set; }
	public Mesh HighSharedMesh { get; set; }
	public Mesh LodSharedMesh { get; set; }
	public Mesh ShadowSharedMesh { get; set; }
	public string HighSharedMeshName { get; set; }
	public string LodSharedMeshName { get; set; }
	public string ShadowSharedMeshName { get; set; }
	public Material[] LodMaterials { get; set; }
	public Material[] ShadowMaterials { get; set; }
	public bool HasLOD { get; }
	public bool IsSkinnedMeshRender { get; set; }
	public string[] HighBoneNames { get; set; }
	public string[] LodBoneNames { get; set; }
	public string[] ShadowBoneNames { get; set; }
	public string MakeFaceTemplateName { get; set; }
	public string MakeFaceTexTemplateName { get; set; }
	public Material[] FaceMaterials { get; set; }
	public bool IsFacePart { get; }
}