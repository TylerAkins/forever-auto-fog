from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class AddonFilesTests(unittest.TestCase):
    def test_toc_declares_expected_metadata_and_load_order(self):
        toc = (ROOT / "ForeverAutoFog.toc").read_text(encoding="utf-8")
        self.assertIn("## Interface: 16001", toc)
        self.assertIn("## SavedVariables: ForeverAutoFogDB", toc)
        self.assertLess(toc.index("Zones.lua"), toc.index("Core.lua"))
        self.assertLess(toc.index("Core.lua"), toc.index("Options.lua"))

    def test_core_uses_only_event_driven_fog_updates(self):
        core = (ROOT / "Core.lua").read_text(encoding="utf-8")
        self.assertIn('C_CVar.SetCVar(FOG_CVAR, desired)', core)
        self.assertIn('C_CVar.GetCVar(FOG_CVAR) ~= desired', core)
        self.assertIn('"ZONE_CHANGED_NEW_AREA"', core)
        self.assertIn('"PLAYER_MAP_CHANGED"', core)
        self.assertIn("parentMapID", core)
        self.assertIn("IsInInstance()", core)
        self.assertNotIn('OnUpdate', core)

    def test_zone_catalog_uses_numeric_map_ids(self):
        zones = (ROOT / "Zones.lua").read_text(encoding="utf-8")
        self.assertRegex(zones, r"mapIDs = \{")
        self.assertNotIn('"Durotar"', zones)

    def test_bulk_controls_and_curseforge_package_metadata_exist(self):
        core = (ROOT / "Core.lua").read_text(encoding="utf-8")
        options = (ROOT / "Options.lua").read_text(encoding="utf-8")
        pkgmeta = (ROOT / ".pkgmeta").read_text(encoding="utf-8")
        self.assertIn("function ns.SetAllPreferences(enabled)", core)
        self.assertIn("ns.SetAllPreferences(true)", options)
        self.assertIn("ns.SetAllPreferences(false)", options)
        self.assertIn('enableAll:SetPoint("TOPLEFT", 16, -110)', options)
        self.assertIn('checkbox.Text:SetText(zone.name)', options)
        self.assertNotIn('zone.name .. ": Enable Fog"', options)
        self.assertIn("package-as: ForeverAutoFog", pkgmeta)

    def test_release_notes_match_version(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        notes = (ROOT / "RELEASE_NOTES.md").read_text(encoding="utf-8")
        self.assertEqual(re.findall(r"^## (\d+\.\d+\.\d+)", notes, re.M), [version])
        self.assertEqual(1, notes.count("## "))


if __name__ == "__main__":
    unittest.main()
