using UnityEngine;
using System;
using System.Collections.Generic;

public class MUMaterialForFashionColor // TypeDefIndex: 5268
{
	// Fields
	[SerializeField]
	public string ColorName; // 0x10
	[SerializeField]
	public Material[] RecordMaterials; // 0x18
}
// Namespace: 
public enum EActorMeshLevel // TypeDefIndex: 4641
{
	high = 0,
	lod = 1,
	shadow = 2
}
// Namespace: MUEngine
public enum EMaterialType // TypeDefIndex: 5265
{
	Default = 0,
	UI = 1,
	Silhouette = 2,
	BlueLight = 3,
	FakeShadow = 4,
	RoleHide = 5,
	RoleHidePrepass = 6,
	RoleHideSelf = 7,
	RoleHideMobile = 8,
	ObjectSelect = 9,
	Transparent = 10,
	RoleTL = 11,
	BossShadow = 12,
	Story1 = 13,
	Story2 = 14,
	Story3 = 15,
	Hologram = 16,
	changeFashion = 17,
	NutrientDefault = 18,
	NutrientBlue = 19,
	NutrientPurple = 20,
	NutrientOrange = 21,
	NutrientCyan = 22,
	Custom1 = 23,
	Custom2 = 24,
	Custom3 = 25,
	Custom4 = 26,
	Custom5 = 27,
	Custom6 = 28,
	Custom7 = 29,
	Custom8 = 30,
	Custom9 = 31,
	Custom10 = 32
}


// Namespace: 
public enum EMeshFuncType // TypeDefIndex: 4642
{
	none = 0,
	face = 1,
	eye = 2,
	personabluefix = 3
}
public class MUMaterialGroup // TypeDefIndex: 5267
{
	// Fields
	[SerializeField]
	private EMaterialType _materialType; // 0x10
	[SerializeField]
	public Material[] RecordMaterials; // 0x18
}

public class ActorMeshMaterialData : MonoBehaviour
{
	public EActorMeshLevel mMeshLevel; // 0x20
	public EMeshFuncType mMeshFuncType; // 0x24
	public float PersonaBlueAlphaFix; // 0x28
	public bool mIsParticleSystem; // 0x2C
	public float OldPersonaBlueAlphaFix; // 0x30
	[SerializeField]
	public List<MUMaterialForFashionColor> MaterialColors; // 0x38
	[SerializeField]
	public List<MUMaterialGroup> HighMaterialGroups; // 0x40
	[SerializeField]
	public List<MUMaterialGroup> LodMaterialGroups; // 0x48
	[SerializeField]
	public List<MUMaterialGroup> ShadowMaterialGroups; // 0x50
	[SerializeField]
	public List<MUMaterialForFashionColor> HighMaterialForFashionColorGroups; // 0x58
	[SerializeField]
	public List<MUMaterialForFashionColor> LodMaterialForFashionColorGroups; // 0x60
	[SerializeField]
	public List<Material> FurMaterialsLow; // 0x68
	[SerializeField]
	public List<Material> FurMaterialsHigh; // 0x70
	[SerializeField]
	public Renderer RecordRenderer; // 0x78
	public bool IsShadowMesh; // 0x80
	public Action MaterialsChanged; // 0x88
	public Action OnNoticeFurEffect; // 0x90
	private EMaterialType _materialType; // 0x98
	private string _colorName; // 0xA0
	private MUMaterialGroup _defaultMaterialGroup; // 0xA8

	// Properties
	public List<MUMaterialGroup> MaterialGroups { get; }
	public List<MUMaterialForFashionColor> MaterialForFashionColor { get; }
	public bool IsLowMesh { get; }
	public bool IsHighMesh { get; }
	public EMaterialType MaterialType { get; set; }
	public string ColorName { get; set; }
	private MUMaterialGroup DefaultMaterialGroup { get; }
}