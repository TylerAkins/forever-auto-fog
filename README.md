# Forever Auto Fog

**Deprecated** for current World of Warcraft Forever builds.

Blizzard removed the client setting that allowed disabling volumetric fog in the [September 24, 2026 beta development notes](https://us.forums.blizzard.com/en/wow/t/wow-forever-beta-development-notes-%E2%80%93-updated-september-24/2360696) (“Removed a setting that could disable fog in an unintended manner”). Forever Auto Fog relied on the `volumeFog` CVar; it has no effect on builds that no longer expose that control. Older Forever builds that still support `volumeFog` may continue to use the last release.

Forever Auto Fog remembered whether volumetric fog should be enabled for each outdoor zone, then applied that preference when you traveled. Fresh installs left fog enabled everywhere, matching the game default.

## Requirements

- World of Warcraft **Forever** only (not Retail, Classic Era, or Cataclysm Classic)
- Folder name must be exactly `ForeverAutoFog`
- No other addons required

## Install

**GitHub:** download a `ForeverAutoFog-v*-forever.zip` file from [GitHub Releases](https://github.com/TylerAkins/forever-auto-fog/releases), not GitHub's automatically generated “Source code” archives.

**CurseForge:** the repository includes CurseForge-compatible `.pkgmeta` packaging. Once its CurseForge project is created, install Forever Auto Fog through the CurseForge client with the Forever game flavor selected.

Extract the zip so the folder is `ForeverAutoFog`, copy it into `Interface\\AddOns\\`, then restart the game or `/reload`. Enable the addon at character select if needed.

## Settings

Open **Escape → Options → AddOns → Forever Auto Fog**. The scrollable **Enable Fog** list is grouped by continent and localized by the game client. A checked zone enables `volumeFog`; an unchecked zone disables it. Changing the current zone applies immediately. **Enable All**, **Disable All**, and **Reset All to Default** update the supported outdoor zones at once; reset restores fog to enabled everywhere.

The addon intentionally excludes cities and instances. `volumeFog` is managed for outdoor world-zone maps only.

Forever continues to add zones. If the client reports an outdoor map that is not in the shipped catalog, Forever Auto Fog treats it as enabled by default, applies that safe default, and exposes the live map ID through `/faf status` and the options panel while you are there.

## Commands

| Command | Action |
|---|---|
| `/faf` | Open settings |
| `/faf on` | Enable fog for the current zone |
| `/faf off` | Disable fog for the current zone |
| `/faf status` | Print the current zone, map ID, saved preference, and CVar value |
| `/faf reset` | Reset every zone to fog enabled |

## Development

Run the local validation suite with:

```sh
python3 -m unittest discover -s tests
```

WoW Forever **Interface** bumps were previously handled by the [Update Forever interface](.github/workflows/update-forever-interface.yml) GitHub Action on a weekly schedule. That schedule is turned off while the addon is deprecated; the workflow remains available for manual `workflow_dispatch` runs if compatibility maintenance resumes.

## License

Addon code is [GPLv3](LICENSE).
